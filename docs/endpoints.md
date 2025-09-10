# GitHub API Endpoints Summary

This project integrates with the GitHub REST API to fetch and analyze Pull Request data.

---

## Authentication
- **Method**: Personal Access Token (PAT)  
- **Header**: `Authorization: token $GITHUB_TOKEN`

---

## Endpoints Used

### 1. List Pull Requests
- **Endpoint**:  
  `GET /repos/{owner}/{repo}/pulls?state=closed&per_page=100`  
- **Use**: Retrieve all pull requests, filtered by `state=closed`.  
- **Docs**: [List pull requests](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests)

---

### 2. Get Reviews for a Pull Request
- **Endpoint**:  
  `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews`  
- **Use**: Check if at least one review has an `"APPROVED"` state.  
- **Docs**: [List reviews](https://docs.github.com/en/rest/pulls/reviews#list-reviews-for-a-pull-request)

---

### 3. Get Combined Status for a Commit
- **Endpoint**:  
  `GET /repos/{owner}/{repo}/commits/{ref}/status`  
- **Use**: Validate whether all required status checks have passed.  
- **Docs**: [Get the combined status for a specific reference](https://docs.github.com/en/rest/commits/statuses#get-the-combined-status-for-a-specific-reference)

---

## Notes
- Pagination is handled via the `?page=` query parameter.  
- Rate limiting: 5000 requests/hour with authentication.  

## ✅ Summary
- **Pull request data**: fetched from `/pulls`
- **Reviews data**: fetched from `/pulls/{number}/reviews`
- **Status checks**: fetched from `/commits/{sha}/status`
- Authentication handled via **PAT** in `Authorization: Bearer` header
