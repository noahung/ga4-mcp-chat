# Product Requirements Document — GA4 MCP Chat

## 1. Overview
Build an internal-use chat interface that allows authorised users to query Google Analytics 4 data across all properties accessible to our Google account.  
The app will use the [Google Analytics MCP Server](https://github.com/googleanalytics/google-analytics-mcp) as a backend data source and a simple password-protected front-end.  
The front-end will be hosted for free on GitHub Pages:  
https://noahung.github.io/ga4-mcp-chat/  

## 2. Goals
- Provide a conversational interface to GA4 data.
- Allow natural language queries like “What was the bounce rate yesterday?” or “Top 10 landing pages last week”.
- Require a shared password for access.
- Keep it internal and lightweight.
- Make deployment and hosting simple.

## 3. Non-Goals
- No OAuth or user-specific logins.
- No public anonymous access.
- No write/update operations to GA4 — read-only analytics.

## 4. Architecture
### 4.1 Components
1. **Frontend (GitHub Pages)**
   - Static HTML/CSS/JS
   - Chat-style interface
   - Password form before showing chat
   - Calls backend API via HTTPS

2. **Backend API (Hosted elsewhere)**
   - Exposes `/query` endpoint
   - Accepts POST request with:
     ```json
     { "password": "...", "message": "..." }
     ```
   - Validates password against an environment variable.
   - Forwards `message` to local MCP server process.
   - Returns MCP server’s response.

3. **Google Analytics MCP Server**
   - Runs on same server as Backend API.
   - Configured with:
     - Google Cloud project with GA Admin + Data API enabled.
     - Application Default Credentials or service account with `analytics.readonly` scope.
   - Supports:
     - `run_report`
     - `run_realtime_report`
     - Account/property introspection

### 4.2 Hosting
- **Frontend** → GitHub Pages (free, public)
- **Backend + MCP server** → Deployed on free tier hosting that supports Python (e.g., Render, Railway, Fly.io, Cloud Run)
