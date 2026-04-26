# Phase 5 — Edge Cases & Failure Modes

## Deployment
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 1 | **Render free tier cold start** | First request after inactivity may take 30-60s. The agent's MCP client should have a generous timeout (90s) for the first call. |
| 2 | **Render deployment fails** | Check Render build logs. Common issues: missing `package.json` scripts, Node version mismatch. Fix and redeploy. |
| 3 | **`credentials.json` has wrong scopes** | Docs/Gmail tools will return 403 errors. Regenerate credentials with the correct scopes (Docs API + Gmail API). |

## OAuth / Token
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 4 | **`token.json` expires** | Google OAuth refresh tokens are long-lived but can expire if unused for 6 months or if the user revokes access. Monitor for 401 errors from the MCP server and re-authenticate. |
| 5 | **Token is for a different Google account** | All Docs/Gmail operations will happen on the wrong account. Verify by checking the "me" profile before deployment. |
| 6 | **Google API quota exceeded** | Default quotas are generous for weekly use. If hit, request quota increase in Google Cloud Console. |

## Network & Availability
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 7 | **Render server is down** | Agent should retry MCP connection 2 times. If still failing, log the error and exit. Do not record as "delivered". |
| 8 | **MCP server returns malformed responses** | Validate the response schema. Log the raw response for debugging. Treat as a failure. |
| 9 | **SSL certificate issues** | Render provides auto-SSL. If expired, Render typically auto-renews. Alert if cert errors appear. |
