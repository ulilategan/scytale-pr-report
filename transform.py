"""
Code for Ulrich Lategan | Scytale Home Assignment
transform.py
- Read the raw JSON files produced by extract.py under outputs/raw/
- Compute per-PR:
    PR number, title, author, merge_date,
    CR_PASSED (approved by >=1 reviewer),
    CHECKS_PASSED (combined status == success)
- Optional filters by merge date (since/until).
- Write outputs/processed/report.csv (and optionally parquet)

Usage:
     python3 transform1.py --in outputs/raw --out outputs/processed/report.csv --parquet 
"""
import os
import json
import argparse
import logging
import pandas as pd
from datetime import datetime
from dateutil import parser as dtparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def pr_summary(pr_dir):
    pr = load_json(os.path.join(pr_dir, "pr.json"))
    reviews = load_json(os.path.join(pr_dir, "reviews.json"))
    status = load_json(os.path.join(pr_dir, "commit_status.json"))

    pr_number = pr.get("number")
    title = pr.get("title") or ""
    author = pr.get("user", {}).get("login") if pr.get("user") else ""
    merge_date = pr.get("merged_at")

    # compute CR_PASSED
    cr_passed = False
    if isinstance(reviews, list):
        cr_passed = any(r.get("state", "").upper() == "APPROVED" for r in reviews)

    # compute CHECKS_PASSED
    checks_passed = False
    if isinstance(status, dict):
        combined = status.get("state")
        checks_passed = (combined == "success")

    return {
        "PR_NUMBER": pr_number,
        "PR_TITLE": title,
        "AUTHOR": author,
        "MERGE_DATE": merge_date,
        "CR_PASSED": cr_passed,
        "CHECKS_PASSED": checks_passed
    }

def filter_by_date(rows, since=None, until=None):
    """Filter rows based on merge_date (ISO strings)."""
    if not since and not until:
        return rows
    filtered = []
    for r in rows:
        if not r["MERGE_DATE"]:
            continue
        merged_at = dtparser.parse(r["MERGE_DATE"])
        if since and merged_at < since:
            continue
        if until and merged_at > until:
            continue
        filtered.append(r)
    return filtered

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_dir", default="outputs/raw")
    parser.add_argument("--out", dest="output_file", default="outputs/processed/report.csv")
    parser.add_argument("--parquet", action="store_true", help="Also write parquet")
    parser.add_argument("--since", help="Only include PRs merged after this date (YYYY-MM-DD)")
    parser.add_argument("--until", help="Only include PRs merged before this date (YYYY-MM-DD)")
    args = parser.parse_args()

    since = datetime.fromisoformat(args.since) if args.since else None
    until = datetime.fromisoformat(args.until) if args.until else None

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)

    items = os.listdir(args.input_dir)
    pr_dirs = [
        os.path.join(args.input_dir, it)
        for it in items if it.startswith("pr_") and os.path.isdir(os.path.join(args.input_dir, it))
    ]

    rows = []
    for pd_ in pr_dirs:
        try:
            rows.append(pr_summary(pd_))
        except Exception as e:
            logging.warning("Skipping %s due to error: %s", pd_, e)

    if not rows:
        logging.warning("No PR data found in %s", args.input_dir)
        return

    rows = filter_by_date(rows, since, until)
    logging.info("Processing %d PRs after filtering", len(rows))

    if not rows:
        logging.warning("No PRs left after date filtering")
        return

    df = pd.DataFrame(rows)
    df = df[["PR_NUMBER", "PR_TITLE", "AUTHOR", "MERGE_DATE", "CR_PASSED", "CHECKS_PASSED"]]
    df["MERGE_DATE"] = df["MERGE_DATE"].apply(lambda x: dtparser.parse(x).isoformat() if x else None)
    df = df.sort_values("MERGE_DATE", ascending=False)

    df.to_csv(args.output_file, index=False)
    logging.info("Wrote CSV to %s", args.output_file)

    if args.parquet:
        ppath = os.path.splitext(args.output_file)[0] + ".parquet"
        df.to_parquet(ppath, index=False)
        logging.info("Wrote Parquet to %s", ppath)

if __name__ == "__main__":
    main()
