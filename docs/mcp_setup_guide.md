# Phase 5: MCP Server Deployment (Manual Steps)

To allow the AI Agent to securely edit Google Docs and send Gmails without storing your Google passwords, we use an external **Model Context Protocol (MCP)** server. I have already cloned the repository for this server to `saksham-mcp-server/`.

Because this involves your private Google Account, **you must complete these steps manually**.

---

### Step 1: Create Google Cloud Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a New Project (e.g., "Groww Pulse MCP").
3. Go to **APIs & Services > Library** and enable two APIs:
   - **Google Docs API**
   - **Gmail API**
4. Go to **APIs & Services > OAuth consent screen**:
   - Choose **External** (or Internal if you have a Workspace).
   - Fill in required app names and emails.
   - Add yourself as a Test User.
5. Go to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth client ID**.
   - Application type: **Desktop app**.
   - Download the JSON file and save it as `credentials.json` inside the `saksham-mcp-server/` folder.

---

### Step 2: Generate the OAuth Token (`token.json`)

You need to authorize the app once to generate a refresh token.

*Note: You need Node.js installed on your machine for this step.*
1. Open a terminal and navigate to `saksham-mcp-server/`.
2. Run `npm install`
3. Run `npm run build`
4. Run `npm start`
5. A browser window will open asking you to sign in with Google. Accept the permissions.
6. The server will generate a file called `token.json`. **Keep this file safe!**

---

### Step 3: Deploy to Render

Now we put the server on the internet so the AI Agent can talk to it.

1. Go to [Render.com](https://render.com/) and sign in with GitHub.
2. Click **New > Web Service** and connect the `saksham-mcp-server` repository.
3. Use the following settings:
   - Environment: `Node`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
4. **Environment Variables**: You must securely upload the contents of your Google keys so Render can use them. Add the following as Environment Variables (or Secret Files if your repo supports it):
   - `GOOGLE_CLIENT_ID`: (From your `credentials.json`)
   - `GOOGLE_CLIENT_SECRET`: (From your `credentials.json`)
   - `GOOGLE_REFRESH_TOKEN`: (From your `token.json`)

### Step 4: Verification

Once Render says the deployment is successful, you will get a URL (e.g., `https://saksham-mcp-server.onrender.com/`). Let me know when you have this URL, and we will proceed to **Phase 6** to connect the AI Agent!
