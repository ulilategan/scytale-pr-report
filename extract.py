"""
Code for Ulrich Lategan | Scytale Home Assignment
extract.py
- Fetch merged PRs from a single repository and save raw JSON into outputs/raw/
- Also fetch reviews and combined commit status per PR and save alongside.
- Handles pagination of the GitHub API.

Usage:
  GITHUB_TOKEN must be in env.
  python3 extract.py --owner Scytale-exercise --repo scytale-repo3 --out outputs/raw --per_page 100
"""
import os
import json
import time
import argparse
import logging
import requests
from tqdm import tqdm

API_BASE = "https://api.github.com"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def gh_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "scytale-pr-report-script"
    }

def paginate_get(session, url, params=None):
    results = []
    while url:
        resp = session.get(url, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"GET {url} returned {resp.status_code}: {resp.text}")
        page = resp.json()
        if isinstance(page, list):
            results.extend(page)
        else:
            results.append(page)

        # look for Link header
        link = resp.headers.get("Link")
        url = None
        if link:
            for p in link.split(","):
                if 'rel="next"' in p:
                    url = p[p.find("<")+1:p.find(">")]
                    break
        params = None  # only apply to first call
        time.sleep(0.1)  # respect rate limits
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True, help="Repository owner/org")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--out", default="outputs/raw", help="Directory to save raw JSON")
    parser.add_argument("--per_page", type=int, default=50, help="Results per page (max 100)")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN environment variable before running.")

    session = requests.Session()
    session.headers.update(gh_headers(token))

    os.makedirs(args.out, exist_ok=True)

    pulls_url = f"{API_BASE}/repos/{args.owner}/{args.repo}/pulls"
    params = {"state": "closed", "per_page": args.per_page}

    logging.info("Fetching closed pull requests...")
    pulls = paginate_get(session, pulls_url, params=params)

    merged_pulls = [p for p in pulls if p.get("merged_at")]
    logging.info(f"Found {len(merged_pulls)} merged PR(s).")

    #Save merged pull list
    with open(os.path.join(args.out, "merged_pulls.json"), "w", encoding="utf-8") as f:
        json.dump(merged_pulls, f, indent=2, ensure_ascii=False)

    #for each merged PR, fetch reviews and commit status
    for p in tqdm(merged_pulls, desc="Processing PRs"):
        pr_num = p["number"]
        pr_dir = os.path.join(args.out, f"pr_{pr_num}")
        os.makedirs(pr_dir, exist_ok=True)

        #Save PR raw
        with open(os.path.join(pr_dir, "pr.json"), "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)

        #Fetch reviews
        reviews_url = f"{API_BASE}/repos/{args.owner}/{args.repo}/pulls/{pr_num}/reviews"
        reviews = paginate_get(session, reviews_url, params={"per_page": args.per_page})
        with open(os.path.join(pr_dir, "reviews.json"), "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)

        #fetch combined status for merge_commit_sha
        merge_sha = p.get("merge_commit_sha")
        status = {}
        if merge_sha:
            status_url = f"{API_BASE}/repos/{args.owner}/{args.repo}/commits/{merge_sha}/status"
            r = session.get(status_url)
            if r.status_code == 200:
                status = r.json()
            else:
                status = {"error": f"{r.status_code}: {r.text}"}
        with open(os.path.join(pr_dir, "commit_status.json"), "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

        time.sleep(0.1)

    logging.info("Yay, extract complete. Raw files under %s", args.out)

if __name__ == "__main__":
    main()
