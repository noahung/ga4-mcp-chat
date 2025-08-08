# GA4 MCP Chat

A terminal-style chat interface for querying Google Analytics 4 data using natural language. This project uses the [Google Analytics MCP Server](https://github.com/googleanalytics/google-analytics-mcp) as a backend data source.

## Project Structure

- **Frontend**: Static HTML/CSS/JS chat interface with a terminal-style aesthetic, hosted on GitHub Pages
- **Backend**: FastAPI (Python) API server that connects to the Google Analytics MCP Server

## Features

- Conversational interface to GA4 data
- Natural language queries (e.g., "What was the bounce rate yesterday?")
- Password-protected access
- Terminal-style UI with typewriter effect and command history
- Responsive design

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (optional, for local frontend development)
- Google Analytics MCP Server installed and configured
- Google Cloud project with GA Admin + Data API enabled
- Application Default Credentials or service account with `analytics.readonly` scope

### Backend Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/noahung/ga4-mcp-chat.git
   cd ga4-mcp-chat
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install and configure the Google Analytics MCP Server:
   ```bash
   pip install google-analytics-mcp
   ```

4. Set up environment variables:
   ```bash
   # Create a .env file in the backend directory
   echo "CHAT_PASSWORD=your_secure_password" > .env
   echo "ENVIRONMENT=production" >> .env
   ```

5. Run the backend server locally:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Update the `BACKEND_URL` in `frontend/app.js` to point to your deployed backend:
   ```javascript
   const BACKEND_URL = "https://your-backend-url.com/query";
   ```

2. For local testing, you can use a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 3000
   ```

3. Access the frontend at `http://localhost:3000`

## Deployment

### Frontend Deployment (GitHub Pages)

1. Create a GitHub repository named `ga4-mcp-chat`

2. Push the `frontend` directory to the `gh-pages` branch:
   ```bash
   git subtree push --prefix frontend origin gh-pages
   ```

3. The frontend will be available at `https://yourusername.github.io/ga4-mcp-chat/`

### Backend Deployment

The backend can be deployed to various platforms:

#### Option 1: Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the build command: `pip install -r backend/requirements.txt`
4. Set the start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `CHAT_PASSWORD` and `ENVIRONMENT=production`

#### Option 2: Google Cloud Run

1. Create a Dockerfile in the backend directory:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
   ```

2. Build and deploy to Cloud Run:
   ```bash
   cd backend
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ga4-mcp-chat
   gcloud run deploy ga4-mcp-chat --image gcr.io/YOUR_PROJECT_ID/ga4-mcp-chat --platform managed
   ```

## Security Considerations

- The frontend is publicly accessible, but the chat functionality is protected by a password
- CORS is restricted to the GitHub Pages domain
- The backend validates the password for each request
- No sensitive GA4 data is stored in the frontend

## License

MIT