# AfriClimate Analytics - Submission Notes

## Dashboard Access
- Local: `http://127.0.0.1:8050`
- Deployed: `https://kutlwano-take-africlimate-analytics-eight.vercel.app/`

## Delivered Components
- `app.py`: Dash dashboard with 5 analytics modules
- `api/index.py`: Vercel Python serverless entrypoint
- `vercel.json`: Vercel routing config
- `requirements.txt`: Python dependencies
- `sql-queries/`: Athena SQL for climate analytics
- `extensions/`: optional advanced analytics modules

## Deployment Configuration
- Deployment target: Vercel (Framework Preset: `Other`, Root Directory: `./`)
- Runtime data mode: `FORCE_FALLBACK_DATA=true` for guaranteed visible data
- Python version pinned in `.python-version`

## Security Controls
- Secrets are not hardcoded in source.
- `.env` files with real credentials are excluded from git.
- Pre-push secret scan process documented in `SECURITY.md`.
