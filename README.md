# AfriClimate Analytics Lake

Serverless climate analytics project for Southern Africa, using AWS data services and a Dash dashboard.

## Live Dashboard
- URL: `https://africlimate-analytics-lake.onrender.com`

## Core Stack
- Data storage/catalog/query: AWS S3, Glue, Athena
- App: Dash + Plotly
- Hosting: Render (`gunicorn app:server`)

## Repository Structure
- `app.py`: Dash application (main entrypoint)
- `render.yaml`: Render service configuration
- `requirements.txt`: Python dependencies
- `.env.example`: environment variable template
- `sql-queries/`: Athena SQL queries
- `extensions/`: optional extension modules
- `scripts/`: utility scripts
- `SUBMISSION_PACKAGE/`: submission-specific artifacts

## Local Run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:8050`

## Deployment (Render)
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:server --workers 1 --threads 2 --timeout 120`
- Python Version: `3.11.9` (pinned in `.python-version`)

### Required Environment Variables
- `FORCE_FALLBACK_DATA=true` (recommended for guaranteed dashboard data)
- `DASH_DEBUG_MODE=false`

### Optional AWS Variables (only when Athena mode is needed)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

If you want live Athena queries, set:
- `FORCE_FALLBACK_DATA=false`

## Security
- No hardcoded credentials are required in source code.
- Keep secrets only in runtime environment variables (Render dashboard / local `.env`, never commit `.env`).
- See `SECURITY.md` for pre-push checks and incident steps.

## Project Status
- Dashboard callbacks wired and verified.
- Fallback dataset enabled by default to avoid empty dashboards during submission/demo.
- Render deployment configured and running via Gunicorn.
