# AfriClimate Analytics - Submission Notes

## Dashboard Access
- Local: `http://127.0.0.1:8050`
- Deployed: `https://africlimate-analytics-lake.onrender.com`

## Delivered Components
- `app.py`: Dash dashboard with 5 analytics modules
- `render.yaml`: Render deployment config
- `requirements.txt`: Python dependencies
- `sql-queries/`: Athena SQL for climate analytics
- `extensions/`: optional advanced analytics modules

## Deployment Configuration
- Start command: `gunicorn app:server --workers 1 --threads 2 --timeout 120`
- Runtime data mode: `FORCE_FALLBACK_DATA=true` for guaranteed visible data
- Python version pinned in `.python-version`

## Security Controls
- Secrets are not hardcoded in source.
- `.env` files with real credentials are excluded from git.
- Pre-push secret scan process documented in `SECURITY.md`.
