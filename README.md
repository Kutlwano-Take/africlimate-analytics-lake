# AfriClimate Analytics Platform

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Dash](https://img.shields.io/badge/Dash-Plotly-0A66C2)
![AWS](https://img.shields.io/badge/Cloud-AWS-orange)
![Deploy](https://img.shields.io/badge/Deploy-Vercel-black)
![License](https://img.shields.io/badge/License-MIT-green)

Production-style climate intelligence dashboard for African rainfall analytics, built to showcase end-to-end data engineering, serverless cloud architecture, and decision-ready analytics.

## Live Product

- Production URL: `https://kutlwano-take-africlimate-analytics-eight.vercel.app/`
- Runtime: Dash on Vercel serverless functions
- Primary data source: CHIRPS rainfall observations
- Cloud architecture: S3, Lambda ETL, Glue Data Catalog, Athena, Dash

## Executive Summary

AfriClimate Analytics Platform turns rainfall data into an interactive climate intelligence product aimed at governments, NGOs, researchers, and climate-risk teams. The application is designed as a modern SaaS-style dashboard rather than a classroom visualization, with emphasis on:

- production-grade dashboard UX
- serverless AWS data engineering
- resilience through fallback data mode
- clear storytelling around climate signals and anomalies
- recruiter-facing presentation of cloud, backend, and analytics skills

## What The Platform Does

- Surfaces rainfall trends, anomaly signals, drought pressure, and visible coverage areas
- Lets users filter by region, time window, and drought condition lens
- Presents insight-driven dashboard cards instead of raw charts alone
- Explains the underlying cloud pipeline directly in the product experience
- Highlights data freshness, live system status, and operational context

## Architecture

The product is backed by a serverless analytics pipeline designed to keep infrastructure simple, scalable, and cost-aware.

![Architecture](docs/architecture.png)

```mermaid
flowchart LR
    A[CHIRPS Climate Data] --> B[Amazon S3 Raw Zone]
    B --> C[AWS Lambda ETL]
    C --> D[Processed Storage Layer]
    D --> E[AWS Glue Data Catalog]
    E --> F[Amazon Athena]
    F --> G[Dash Analytics App]
    G --> H[Vercel Deployment]
```

### Architecture Goals

- Serverless by default: no always-on application servers or query infrastructure
- Scalable analytics: schema-on-read querying through Athena
- Cost efficiency: cloud-native services aligned to event-driven workloads
- Reliability: fallback dataset mode keeps the dashboard available when live cloud access is unavailable

## Product Experience

The current dashboard experience includes:

- A premium landing section with product-style positioning
- Sticky navigation and dark SaaS visual system
- Overview KPI cards for rainfall, anomalies, drought alerts, and coverage
- Interactive rainfall trend, regional comparison, and anomaly charts
- Architecture section that explains the full cloud pipeline visually
- Engineering highlights focused on observability, scale, cost, and resilience
- Use-case framing for agriculture, climate planning, and risk analysis

## Engineering Highlights

- **Serverless pipeline:** CHIRPS rainfall data is processed through S3, Lambda, Glue, and Athena
- **Analytics-first UX:** The dashboard combines filters, insights, and charts into a coherent decision workflow
- **Fallback resilience:** The application defaults to a local resilience dataset for reliable demos and recruiter review
- **Production-oriented design:** Live status, data freshness, operational telemetry, and architecture visibility are built into the UI
- **Deployable portfolio quality:** The app is production-hosted and structured for public review

## Technology Stack

### Data & Cloud

- Amazon S3
- AWS Lambda
- AWS Glue
- Amazon Athena
- CloudWatch
- IAM

### Application Layer

- Python 3.12
- Dash
- Plotly
- Pandas
- NumPy
- Boto3

### Deployment

- Vercel

## Repository Structure

```text
.
├── app.py                    # Main Dash application
├── api/index.py              # Vercel serverless entrypoint
├── assets/dashboard.css      # Custom dashboard styling
├── vercel.json               # Vercel routing configuration
├── requirements.txt          # Python dependencies
├── docs/                     # Documentation assets
├── sql-queries/              # Athena and analytics SQL
├── scripts/                  # Utility and setup scripts
├── extensions/               # Optional feature modules
└── SUBMISSION_PACKAGE/       # Submission-specific artifacts
```

## Running Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

`http://127.0.0.1:8050`

## Runtime Modes

| Mode | Purpose | Configuration |
|---|---|---|
| Fallback Mode | Stable demo and portfolio experience using local resilience data | `FORCE_FALLBACK_DATA=true` |
| Athena Mode | Live cloud-backed query path | `FORCE_FALLBACK_DATA=false` plus AWS credentials |

## Environment Configuration

### Required For Hosted Demo

- `FORCE_FALLBACK_DATA=true`
- `DASH_DEBUG_MODE=false`

### Required For Live AWS Querying

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

## Deployment Notes

This repository is configured for Vercel using a Python serverless entrypoint:

- Framework preset: `Other`
- Root directory: `./`
- Entry point: `api/index.py`
- Python version: pinned through `.python-version`

## Why This Project Matters

AfriClimate Analytics Platform is intentionally positioned as more than a dashboard. It demonstrates:

- backend and cloud architecture thinking
- data engineering workflow design
- product-oriented analytics presentation
- resilience and deployment awareness
- the ability to turn technical infrastructure into a credible real-world data product

## Roadmap

1. Add authenticated user roles and protected views.
2. Expand live data freshness and scheduled ingestion metadata.
3. Introduce alerting workflows for drought and rainfall anomaly thresholds.
4. Add automated tests for callbacks, ETL logic, and deployment health.
5. Reduce dependency footprint to improve Vercel cold starts and build efficiency.

## Security

- Secrets are expected through environment variables only
- `.env`, `.env.local`, and Vercel-local files are excluded from source control
- No production AWS credentials should ever be committed to the repository

## License

MIT
