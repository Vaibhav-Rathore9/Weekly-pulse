# Phase 5 — Evaluation Checklist

## Deployment Tests

### Clone & Setup
- [ ] `git clone https://github.com/saksham20189575/saksham-mcp-server` succeeds.
- [ ] Local `npm install` (or equivalent) completes without errors.
- [ ] Local server starts successfully with `npm start` (or equivalent).

### OAuth Flow
- [ ] `credentials.json` is generated from Google Cloud Console with correct scopes (Docs + Gmail).
- [ ] Running the server locally opens a browser for OAuth consent.
- [ ] After consent, `token.json` is created in the project directory.
- [ ] The token has both `docs` and `gmail` scopes.

### Render Deployment
- [ ] Render Blueprint deployment completes without errors.
- [ ] `credentials.json` and `token.json` are uploaded as Render secret files / environment variables.
- [ ] Server is accessible at `https://saksham-mcp-server.onrender.com/`.
- [ ] Server responds to health check / root endpoint.

### MCP Protocol Verification
- [ ] Sending an MCP `tools/list` request returns a valid JSON response.
- [ ] Response includes a tool for Google Docs operations (e.g., `google_docs_append`, `google_docs_batch_update`, or similar).
- [ ] Response includes a tool for Gmail operations (e.g., `gmail_send`, `gmail_create_draft`, or similar).

### Functional Smoke Test
- [ ] Manually invoke the Docs tool to append text to a test Google Doc. Verify the text appears.
- [ ] Manually invoke the Gmail tool to send a test email. Verify the email is received.
- [ ] Both tools return success responses with identifiers (e.g., document revision, message ID).

## Security
- [ ] `credentials.json` and `token.json` are NOT committed to the Git repository.
- [ ] Render environment variables / secret files are not visible in Render dashboard logs.
- [ ] The MCP server does not expose raw Google credentials in error responses.
