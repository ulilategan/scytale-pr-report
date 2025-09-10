# GitHub PR Review & Checks Report

This project fetches merged pull requests (PRs) from a GitHub repository and checks if they
were approved and passed all required status checks before merging.

It was built as a coding assignment for **Scytale**.

---

## 🚀 Features
- Authenticate with GitHub API using a Personal Access Token (PAT).
- Fetch merged pull requests from a given repository.
- Save raw JSON for each PR (details, reviews, commit status).
- Transform raw data into a structured CSV (and optional Parquet) report.
- Report includes:
  - PR number
  - PR title
  - Author
  - Merge date
  - `CR_PASSED` (was it approved by ≥1 reviewer?)
  - `CHECKS_PASSED` (did all required status checks pass?)
- Handles API pagination.
- Modular code split into `extract.py` (data retrieval) and `transform.py` (data processing).
- Outputs stored in organized subfolders (`outputs/raw` and `outputs/processed`).

---
## 📋 Implementation

This solution consists of two main scripts:

### extract.py
- Fetches merged pull requests from GitHub repositories
- Retrieves PR details, reviews, and commit statuses
- Handles API pagination and rate limiting
- Saves raw JSON data to `outputs/raw/`

### transform.py
- Processes raw JSON data from extract phase
- Computes code review and status check compliance
- Generates CSV/Parquet reports in `outputs/processed/`
- Supports date filtering for analysis

---
## 📦 Requirements
- Set GitHub token:
   ```bash
   export GITHUB_TOKEN=your_personal_access_token
- Python 3.8+
- Packages:
  ```bash
  pip install requests tqdm pandas python-dateutil
