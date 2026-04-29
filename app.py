import os
from datetime import datetime
from zoneinfo import ZoneInfo

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from dotenv import load_dotenv

try:
    import boto3
except Exception:
    boto3 = None

try:
    import awswrangler as wr
except Exception:
    wr = None

load_dotenv()

SAST = ZoneInfo("Africa/Johannesburg")
GITHUB_REPO = "https://github.com/Kutlwano-Take/africlimate-analytics-lake"
CONTACT_URL = "https://github.com/Kutlwano-Take"

PROVINCE_META = {
    "Gauteng": {"lat": -26.2041, "lon": 28.0473, "factor": 0.82, "trend": -0.8, "cluster": "Economic Core", "exposure": 18},
    "Limpopo": {"lat": -23.4013, "lon": 29.4179, "factor": 0.96, "trend": -1.4, "cluster": "Northern Belt", "exposure": 21},
    "Mpumalanga": {"lat": -25.5653, "lon": 30.5279, "factor": 1.04, "trend": -0.5, "cluster": "Escarpment Belt", "exposure": 16},
    "KwaZulu-Natal": {"lat": -29.8587, "lon": 31.0218, "factor": 1.12, "trend": 0.4, "cluster": "Eastern Seaboard", "exposure": 13},
    "Eastern Cape": {"lat": -32.2968, "lon": 26.4194, "factor": 0.9, "trend": -0.6, "cluster": "Coastal South", "exposure": 17},
    "Western Cape": {"lat": -33.9249, "lon": 18.4241, "factor": 0.76, "trend": -1.0, "cluster": "Coastal South", "exposure": 20},
    "Northern Cape": {"lat": -29.0467, "lon": 21.8569, "factor": 0.52, "trend": -1.8, "cluster": "Semi-Arid West", "exposure": 28},
    "North West": {"lat": -26.6639, "lon": 25.2838, "factor": 0.64, "trend": -1.3, "cluster": "Central Plateau", "exposure": 24},
    "Free State": {"lat": -28.4541, "lon": 26.7968, "factor": 0.7, "trend": -1.1, "cluster": "Central Plateau", "exposure": 22},
}

NAV_LINKS = [
    ("Overview", "#overview"),
    ("Dashboard", "#dashboard"),
    ("Architecture", "#architecture"),
    ("Highlights", "#highlights"),
    ("Use Cases", "#use-cases"),
]

PIPELINE_STEPS = [
    {"code": "SRC", "label": "CHIRPS", "sub": "Satellite rainfall source"},
    {"code": "S3", "label": "Amazon S3", "sub": "Raw and processed lake"},
    {"code": "ETL", "label": "AWS Lambda", "sub": "Event-driven transforms"},
    {"code": "CAT", "label": "AWS Glue", "sub": "Catalog and schema tracking"},
    {"code": "SQL", "label": "Athena", "sub": "Serverless analytics layer"},
    {"code": "APP", "label": "Dashboard", "sub": "Dash and Plotly experience"},
]

FEATURES = [
    {"code": "RT", "title": "Near real-time analytics", "description": "Event-driven processing keeps decision dashboards synchronized with newly published rainfall slices."},
    {"code": "FX", "title": "Interactive filtering", "description": "Slice by geography, time window, and drought condition without losing context across the rest of the dashboard."},
    {"code": "SC", "title": "Scalable data pipeline", "description": "Serverless storage, metadata, and query services let the same architecture support both demo slices and larger climate archives."},
    {"code": "FT", "title": "Fault tolerance", "description": "Fallback dataset mode preserves availability when upstream services or credentials are unavailable."},
    {"code": "CO", "title": "Cost optimization", "description": "A schema-on-read design and partition-friendly workflow minimize unnecessary compute and scanned bytes."},
    {"code": "OB", "title": "Observability", "description": "Pipeline health, freshness, and operating mode are surfaced directly in the product experience for fast operator awareness."},
]

STACK_TAGS = [
    "AWS S3",
    "AWS Lambda",
    "AWS Glue",
    "Amazon Athena",
    "CloudWatch",
    "IAM",
    "Python",
    "Dash",
    "Plotly",
    "Pandas",
    "NumPy",
    "Parquet",
    "Boto3",
    "Vercel",
]

USE_CASES = [
    {"code": "AG", "title": "Agricultural planning", "description": "Support irrigation planning, planting calendars, and crop-risk monitoring with consistent rainfall trend signals."},
    {"code": "CP", "title": "Climate planning", "description": "Give researchers and public agencies a durable way to analyze rainfall stress, variability, and long-run anomalies."},
    {"code": "RA", "title": "Risk analysis", "description": "Flag emerging drought pressure and operational hotspots for humanitarian teams, insurers, and resilience programs."},
]

WINDOW_OPTIONS = [
    {"label": "Last 3 months", "value": "3M"},
    {"label": "Last 12 months", "value": "12M"},
    {"label": "Last 24 months", "value": "24M"},
    {"label": "All data", "value": "All"},
]

CONDITION_OPTIONS = [
    {"label": "All conditions", "value": "all"},
    {"label": "High climate risk", "value": "high-risk"},
    {"label": "Severe drought", "value": "severe"},
    {"label": "Extreme drought", "value": "extreme"},
]

WINDOW_LABELS = {item["value"]: item["label"] for item in WINDOW_OPTIONS}
CONDITION_LABELS = {item["value"]: item["label"] for item in CONDITION_OPTIONS}

THEME = {
    "primary": "#22c55e",
    "accent": "#38bdf8",
    "warning": "#fbbf24",
    "success": "#34d399",
    "foreground": "#e2e8f0",
    "muted": "#94a3b8",
    "grid": "rgba(71, 85, 105, 0.25)",
    "hover": "#0f172a",
}


def build_fallback_data():
    rng = np.random.default_rng(42)
    rows = []
    for year in range(2020, 2025):
        for month in range(1, 13):
            seasonal_curve = 96 + 56 * np.cos((month - 2) / 12 * 2 * np.pi)
            storm_bias = 12 if month in {1, 2, 11, 12} else 0
            for province, meta in PROVINCE_META.items():
                for sample in range(4):
                    measurement_noise = rng.normal(0, 13)
                    climate_drift = (year - 2020) * meta["trend"]
                    precipitation = max(
                        6.0,
                        seasonal_curve * meta["factor"] + storm_bias + climate_drift + measurement_noise,
                    )
                    rows.append(
                        {
                            "latitude": float(meta["lat"] + rng.normal(0, 0.22)),
                            "longitude": float(meta["lon"] + rng.normal(0, 0.22)),
                            "precipitation": float(round(precipitation, 2)),
                            "year": year,
                            "month": month,
                            "day": int(min(28, sample * 7 + rng.integers(1, 7))),
                            "province": province,
                        }
                    )
    return pd.DataFrame(rows)


def infer_area_from_coordinates(row):
    latitude = row.get("latitude")
    longitude = row.get("longitude")
    if pd.isna(latitude) or pd.isna(longitude):
        return "Regional aggregate"
    if latitude < -18 and longitude < 24:
        return "Southern Africa West"
    if latitude < -18 and longitude >= 24:
        return "Southern Africa East"
    if latitude < 5 and longitude < 20:
        return "Central Africa"
    if latitude < 12 and longitude >= 20:
        return "East Africa"
    return "West Africa"


def infer_cluster_from_area(area):
    if "West" in area:
        return "Semi-Arid Belt"
    if "East" in area:
        return "Eastern Corridor"
    if "Central" in area:
        return "Equatorial Belt"
    return "Regional Core"


def season_from_month(month):
    if month in {12, 1, 2}:
        return "Summer"
    if month in {3, 4, 5}:
        return "Autumn"
    if month in {6, 7, 8}:
        return "Winter"
    return "Spring"


def enrich_dataframe(df):
    out = df.copy()

    for column, default in (("year", 2024), ("month", 1), ("day", 1)):
        if column not in out:
            out[column] = default
        out[column] = pd.to_numeric(out[column], errors="coerce").fillna(default).astype(int)

    if "precipitation" not in out:
        out["precipitation"] = 0.0
    out["precipitation"] = pd.to_numeric(out["precipitation"], errors="coerce").fillna(0.0).astype(float)

    if "latitude" not in out:
        out["latitude"] = np.nan
    if "longitude" not in out:
        out["longitude"] = np.nan

    constructed_date = pd.to_datetime(
        {"year": out["year"], "month": out["month"], "day": out["day"]},
        errors="coerce",
    )
    if "date" in out:
        out["date"] = pd.to_datetime(out["date"], errors="coerce").fillna(constructed_date)
    else:
        out["date"] = constructed_date

    inferred_areas = out.apply(infer_area_from_coordinates, axis=1)
    if "province" not in out:
        out["province"] = inferred_areas
    else:
        out["province"] = out["province"].fillna(inferred_areas).astype(str)

    cluster_lookup = {name: meta["cluster"] for name, meta in PROVINCE_META.items()}
    out["cluster"] = out["province"].map(cluster_lookup).fillna(out["province"].map(infer_cluster_from_area))
    out["season"] = out["month"].apply(season_from_month)
    out["year_month"] = out["date"].dt.to_period("M").astype(str)

    monthly_mean = out.groupby("month")["precipitation"].transform("mean")
    monthly_std = out.groupby("month")["precipitation"].transform("std")
    fallback_std = float(out["precipitation"].std()) if float(out["precipitation"].std()) > 0 else 1.0
    anomaly_sigma_divisor = monthly_std.where(monthly_std > 0).fillna(fallback_std)

    out["anomaly_mm"] = out["precipitation"] - monthly_mean
    out["anomaly_sigma"] = out["anomaly_mm"] / anomaly_sigma_divisor

    drought_levels = pd.cut(
        out["precipitation"],
        bins=[-np.inf, 35, 65, 100, np.inf],
        labels=["Extreme", "Severe", "Moderate", "Low"],
    )
    out["drought_level"] = drought_levels.astype(str).replace("nan", "Moderate")

    exposure_lookup = {name: meta["exposure"] for name, meta in PROVINCE_META.items()}
    dry_anomaly = np.maximum(-out["anomaly_sigma"], 0)
    out["climate_risk"] = np.clip(
        (100 - out["precipitation"].clip(upper=100)) * 0.48
        + dry_anomaly * 14
        + out["province"].map(exposure_lookup).fillna(14)
        + np.where(out["season"] == "Summer", 5, 0),
        6,
        99,
    ).round(1)

    out["carbon_emissions"] = (
        42
        + out["climate_risk"] * 0.62
        + out["year"].sub(out["year"].min()) * 3.2
        + np.where(out["drought_level"].isin(["Severe", "Extreme"]), 6, 0)
    ).round(1)
    out["community_impact"] = np.clip(
        out["climate_risk"] * 0.88 + np.where(out["drought_level"].isin(["Severe", "Extreme"]), 10, 0),
        5,
        100,
    ).round(0)

    return out.sort_values("date").reset_index(drop=True)


def load_data():
    base_meta = {
        "loaded_at": datetime.now(SAST),
        "mode": "Fallback dataset mode",
        "source": "Local resilience slice",
        "is_fallback": True,
        "status": "Operational",
        "note": "Guaranteed visibility for demos and recruiter review.",
    }

    if os.getenv("FORCE_FALLBACK_DATA", "true").lower() == "true":
        print("FORCE_FALLBACK_DATA=true; using local fallback data.")
        return enrich_dataframe(build_fallback_data()), base_meta

    if wr is None or boto3 is None:
        print("AWS dependencies unavailable; using local fallback data.")
        return enrich_dataframe(build_fallback_data()), base_meta

    boto3.setup_default_session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "af-south-1"),
    )

    try:
        query = """
        SELECT latitude, longitude, precipitation, year, month, day
        FROM africlimate_climate_db.chirps_data
        WHERE year BETWEEN 2020 AND 2024
        LIMIT 3000
        """
        data = wr.athena.read_sql_query(
            sql=query,
            database="africlimate_climate_db",
            workgroup="primary",
            s3_output="s3://aws-athena-query-results-701742813629-af-south-1/",
        )
        if data.empty:
            return enrich_dataframe(build_fallback_data()), base_meta
        live_meta = {
            "loaded_at": datetime.now(SAST),
            "mode": "Athena live query mode",
            "source": "Amazon Athena over CHIRPS partitions",
            "is_fallback": False,
            "status": "Operational",
            "note": "Serverless query path active.",
        }
        return enrich_dataframe(data), live_meta
    except Exception as exc:
        print(f"ATHENA LOAD ERROR: {exc}")
        fallback_meta = dict(base_meta)
        fallback_meta["note"] = "Primary query path failed, so the dashboard switched to resilience mode."
        return enrich_dataframe(build_fallback_data()), fallback_meta


def badge(text, tone="primary"):
    return html.Span(text, className=f"pill pill-{tone}")


def button_link(label, href, variant="primary", external=False):
    props = {"href": href, "className": f"button-link button-{variant}"}
    if external:
        props["target"] = "_blank"
        props["rel"] = "noreferrer"
    return html.A(label, **props)


def metric_card(code, title, value_id, detail_id, tone):
    return html.Div(
        [
            html.Div(
                [
                    html.Span(code, className="metric-code"),
                    html.P(title, className="metric-label"),
                ],
                className="metric-top",
            ),
            html.P(id=value_id, className="metric-value"),
            html.P(id=detail_id, className=f"metric-detail tone-text-{tone}"),
        ],
        className=f"glass-card metric-card tone-{tone}",
    )


def signal_card(label, value, detail):
    return html.Div(
        [
            html.P(label, className="signal-label"),
            html.P(value, className="signal-value"),
            html.P(detail, className="signal-detail"),
        ],
        className="signal-card",
    )


def throughput_rows(meta):
    telemetry = [
        ("S3 ingest", 94),
        ("Lambda ETL", 88),
        ("Glue catalog", 96),
        ("Athena queries", 81 if not meta["is_fallback"] else 68),
    ]
    if meta["is_fallback"]:
        telemetry[-1] = ("Fallback resilience", 100)

    rows = []
    for label, value in telemetry:
        rows.append(
            html.Div(
                [
                    html.Div(
                        [html.Span(label, className="progress-label"), html.Span(f"{value}%", className="progress-value")],
                        className="progress-head",
                    ),
                    html.Div(html.Div(className="progress-fill", style={"width": f"{value}%"}), className="progress-track"),
                ],
                className="progress-row",
            )
        )
    return rows


def event_item(label, title, detail, tone="primary"):
    return html.Div(
        [
            html.Span(className=f"status-ping tone-bg-{tone}"),
            html.Div(
                [
                    html.Div([html.Span(label, className="event-label"), html.Span(title, className="event-title")], className="event-headline"),
                    html.P(detail, className="event-detail"),
                ],
                className="event-copy",
            ),
        ],
        className="event-row",
    )


def time_coverage_label(df):
    if df["date"].dropna().empty:
        return "Unavailable"
    return f"{df['date'].min().year}-{df['date'].max().year}"


def style_figure(fig, height, show_legend=False):
    fig.update_layout(
        height=height,
        margin={"l": 18, "r": 18, "t": 18, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Manrope, Segoe UI, sans-serif", "color": THEME["foreground"]},
        hoverlabel={"bgcolor": THEME["hover"], "bordercolor": "#334155", "font": {"family": "JetBrains Mono, monospace"}},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0, "font": {"size": 11}},
        showlegend=show_legend,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=THEME["grid"],
        zeroline=False,
        showline=False,
        tickfont={"color": THEME["muted"], "size": 11},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=THEME["grid"],
        zeroline=False,
        showline=False,
        tickfont={"color": THEME["muted"], "size": 11},
    )
    return fig


def empty_figure(message, height):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 14, "color": THEME["muted"], "family": "Manrope, Segoe UI, sans-serif"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_figure(fig, height)


def apply_filters(dataframe, location, window, condition):
    filtered = dataframe.copy()

    if location and location != "All locations":
        filtered = filtered[filtered["province"] == location]

    if condition == "high-risk":
        threshold = filtered["climate_risk"].quantile(0.7) if not filtered.empty else 0
        filtered = filtered[filtered["climate_risk"] >= threshold]
    elif condition == "severe":
        filtered = filtered[filtered["drought_level"].isin(["Severe", "Extreme"])]
    elif condition == "extreme":
        filtered = filtered[filtered["drought_level"] == "Extreme"]

    if filtered.empty:
        return filtered

    months = {"3M": 3, "12M": 12, "24M": 24}.get(window)
    if months:
        valid_dates = filtered["date"].dropna()
        if not valid_dates.empty:
            cutoff = valid_dates.max().to_period("M").to_timestamp() - pd.DateOffset(months=months - 1)
            filtered = filtered[filtered["date"] >= cutoff]

    return filtered.sort_values("date")


def comparison_slice(dataframe, location):
    if location and location != "All locations":
        scoped = dataframe[dataframe["province"] == location]
        if not scoped.empty:
            return scoped
    return dataframe


def safe_pct_delta(current, baseline):
    if baseline is None or pd.isna(baseline) or abs(float(baseline)) < 1e-9:
        return 0.0
    return ((float(current) - float(baseline)) / float(baseline)) * 100


def signed_text(value, suffix, decimals=1):
    return f"{value:+.{decimals}f}{suffix}"


def build_rainfall_figure(filtered, reference):
    if filtered.empty:
        return empty_figure("No rainfall records match the selected filters.", 320)

    monthly = filtered.groupby(pd.Grouper(key="date", freq="MS"))["precipitation"].mean().reset_index()
    baseline_map = reference.groupby("month")["precipitation"].mean()
    monthly["baseline"] = monthly["date"].dt.month.map(baseline_map)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["baseline"],
            mode="lines",
            name="Baseline",
            line={"color": "rgba(148, 163, 184, 0.95)", "width": 2, "dash": "dash", "shape": "spline"},
            hovertemplate="%{x|%b %Y}<br>%{y:.1f} mm<extra>Baseline</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["precipitation"],
            mode="lines+markers",
            name="Observed",
            line={"color": THEME["primary"], "width": 3, "shape": "spline"},
            marker={"size": 7, "color": THEME["primary"], "line": {"width": 0}},
            fill="tozeroy",
            fillcolor="rgba(34, 197, 94, 0.14)",
            hovertemplate="%{x|%b %Y}<br>%{y:.1f} mm<extra>Observed</extra>",
        )
    )
    fig.update_yaxes(title="mm")
    fig.update_xaxes(tickformat="%b\n%Y")
    return style_figure(fig, 320, show_legend=True)


def build_region_figure(filtered):
    if filtered.empty:
        return empty_figure("No regional comparison is available for the selected slice.", 320)

    regional = (
        filtered.groupby("province", as_index=False)["precipitation"]
        .mean()
        .sort_values("precipitation", ascending=False)
    )

    colors = [THEME["accent"]] + ["rgba(56, 189, 248, 0.45)"] * max(len(regional) - 1, 0)
    fig = go.Figure(
        go.Bar(
            x=regional["province"],
            y=regional["precipitation"],
            marker={"color": colors, "line": {"color": "rgba(125, 211, 252, 0.5)", "width": 1}},
            hovertemplate="%{x}<br>%{y:.1f} mm<extra>Average rainfall</extra>",
        )
    )
    fig.update_xaxes(tickangle=-28)
    fig.update_yaxes(title="mm")
    return style_figure(fig, 320)


def build_anomaly_figure(filtered, reference):
    if filtered.empty:
        return empty_figure("No anomaly signal is available for the selected slice.", 120)

    monthly = filtered.groupby(pd.Grouper(key="date", freq="MS"))["precipitation"].mean().reset_index()
    baseline_map = reference.groupby("month")["precipitation"].mean()
    monthly["baseline"] = monthly["date"].dt.month.map(baseline_map)
    monthly["anomaly"] = monthly["precipitation"] - monthly["baseline"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["anomaly"],
            mode="lines",
            line={"color": THEME["warning"], "width": 2.8, "shape": "spline"},
            fill="tozeroy",
            fillcolor="rgba(251, 191, 36, 0.18)",
            hovertemplate="%{x|%b %Y}<br>%{y:+.1f} mm<extra>Anomaly</extra>",
            showlegend=False,
        )
    )
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="rgba(148, 163, 184, 0.65)")
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(title="mm")
    return style_figure(fig, 120)


def build_sidebar(meta, dataframe):
    latest_date = dataframe["date"].max().strftime("%d %b %Y") if not dataframe["date"].dropna().empty else "Unavailable"
    return html.Aside(
        [
            html.Div(
                [
                    html.P("Navigation", className="sidebar-title"),
                    html.Div([html.A(label, href=href, className="side-link") for label, href in NAV_LINKS], className="side-link-list"),
                ],
                className="sidebar-block",
            ),
            html.Div(
                [
                    html.P("Live System Status", className="sidebar-title"),
                    html.Div([html.Span(className="status-ping tone-bg-success"), html.Span(meta["status"], className="sidebar-status-text")], className="sidebar-status-line"),
                    html.Div(className="sidebar-meta-row", children=[html.Span("Data freshness", className="sidebar-meta-label"), html.Span(latest_date, className="sidebar-meta-value")]),
                    html.Div(className="sidebar-meta-row", children=[html.Span("Operating mode", className="sidebar-meta-label"), html.Span(meta["mode"], className="sidebar-meta-value")]),
                    html.Div(className="sidebar-meta-row", children=[html.Span("Clock", className="sidebar-meta-label"), html.Span(id="sidebar-clock", className="sidebar-meta-value")]),
                ],
                className="glass-card sidebar-system-card",
            ),
            html.Div(
                [
                    button_link("View GitHub", GITHUB_REPO, variant="secondary", external=True),
                    button_link("Hire Me / Contact", CONTACT_URL, variant="ghost", external=True),
                ],
                className="sidebar-actions",
            ),
        ],
        className="glass-card side-nav",
    )


def build_hero(meta, dataframe):
    latest_date = dataframe["date"].max().strftime("%d %b %Y") if not dataframe["date"].dropna().empty else "Unavailable"
    pipeline_preview = []
    for index, step in enumerate(PIPELINE_STEPS):
        pipeline_preview.append(
            html.Div(
                [
                    html.Span(step["code"], className="mini-step-code"),
                    html.Div(
                        [
                            html.P(step["label"], className="mini-step-label"),
                            html.P(step["sub"], className="mini-step-sub"),
                        ]
                    ),
                ],
                className="mini-step",
            )
        )
        if index < len(PIPELINE_STEPS) - 1:
            pipeline_preview.append(html.Div(className="mini-arrow"))

    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div([html.Span("CHIRPS climate analytics", className="eyebrow-text")], className="eyebrow-pill"),
                            html.H1(
                                ["AI-Powered ", html.Span("Climate Intelligence", className="text-gradient"), " for Africa"],
                                className="hero-title",
                            ),
                            html.P(
                                "A serverless climate analytics product turning rainfall observations into operational insight for governments, NGOs, and researchers through AWS-native data engineering and an interactive decision dashboard.",
                                className="hero-copy",
                            ),
                            html.Div(
                                [
                                    button_link("Explore the dashboard", "#dashboard", variant="primary"),
                                    button_link("View architecture", "#architecture", variant="secondary"),
                                ],
                                className="hero-actions",
                            ),
                            html.Div(
                                [
                                    html.Div([html.P("CHIRPS v2.0", className="hero-stat-value"), html.P("Rainfall data source", className="hero-stat-label")], className="hero-stat"),
                                    html.Div([html.P("AWS", className="hero-stat-value"), html.P("Serverless pipeline", className="hero-stat-label")], className="hero-stat"),
                                    html.Div([html.P(f"{len(dataframe):,}", className="hero-stat-value"), html.P("Rows rendered in-app", className="hero-stat-label")], className="hero-stat"),
                                    html.Div([html.P(time_coverage_label(dataframe), className="hero-stat-value"), html.P("Accessible time window", className="hero-stat-label")], className="hero-stat"),
                                ],
                                className="hero-stats",
                            ),
                        ],
                        className="hero-copy-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div([html.P("Architecture preview", className="panel-kicker"), html.H3("Serverless climate pipeline", className="panel-title")]),
                                            badge("Operational", tone="success"),
                                        ],
                                        className="panel-head",
                                    ),
                                    html.Div(pipeline_preview, className="mini-pipeline"),
                                    html.Div(
                                        [
                                            signal_card("Data freshness", latest_date, "Latest visible observation"),
                                            signal_card("Deployment", "Dash on Vercel", "Python app with serverless entrypoint"),
                                            signal_card("Mode", meta["mode"], meta["source"]),
                                        ],
                                        className="signal-grid",
                                    ),
                                ],
                                className="glass-card hero-panel",
                            )
                        ],
                        className="hero-side-panel",
                    ),
                ],
                className="hero-grid",
            )
        ],
        id="overview",
        className="hero-section",
    )


def build_dashboard():
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Live dashboard", className="section-kicker"),
                            html.H2("Rainfall intelligence for operational decisions", className="section-title"),
                            html.P(
                                "Move from raw observations to explainable climate signals with filterable analytics, anomaly tracking, and infrastructure-aware storytelling.",
                                className="section-copy",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div([html.Span(className="status-ping tone-bg-success"), html.Span("Live system status", className="status-chip-text")], className="status-chip"),
                            html.Div([html.Span("Data freshness", className="status-chip-label"), html.Span(id="live-clock", className="status-chip-time")], className="status-chip status-chip-secondary"),
                        ],
                        className="section-status-row",
                    ),
                ],
                className="section-header",
            ),
            html.Div(
                [
                    html.Div([html.P("Coverage area", className="filter-label"), dcc.Dropdown(id="location-filter", options=LOCATION_OPTIONS, value="All locations", clearable=False, className="filter-select")], className="filter-field"),
                    html.Div([html.P("Time window", className="filter-label"), dcc.Dropdown(id="window-filter", options=WINDOW_OPTIONS, value="12M", clearable=False, className="filter-select")], className="filter-field"),
                    html.Div([html.P("Condition lens", className="filter-label"), dcc.Dropdown(id="condition-filter", options=CONDITION_OPTIONS, value="all", clearable=False, className="filter-select")], className="filter-field"),
                ],
                className="glass-card filter-grid",
            ),
            html.Div(
                [
                    metric_card("RF", "Mean rainfall", "metric-rainfall-value", "metric-rainfall-detail", "primary"),
                    metric_card("AX", "Anomaly index", "metric-anomaly-value", "metric-anomaly-detail", "accent"),
                    metric_card("DR", "Drought alerts", "metric-alerts-value", "metric-alerts-detail", "warning"),
                    metric_card("RG", "Visible areas", "metric-coverage-value", "metric-coverage-detail", "success"),
                ],
                className="metrics-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.H3("Rainfall trend", className="chart-title"), html.P("Observed monthly precipitation against the historical baseline for the current slice.", className="chart-subtitle")]),
                                    html.Span(id="trend-badge", className="chart-badge"),
                                ],
                                className="chart-head",
                            ),
                            html.Div(id="trend-insight", className="insight-banner"),
                            dcc.Loading(dcc.Graph(id="rainfall-trend", config={"displayModeBar": False, "responsive": True}, className="chart-graph"), color=THEME["primary"]),
                        ],
                        className="glass-card chart-card chart-card-large",
                    ),
                    html.Div(
                        [
                            html.H3("Regional comparison", className="chart-title"),
                            html.P("Average rainfall intensity by visible area.", className="chart-subtitle"),
                            dcc.Loading(dcc.Graph(id="regional-bars", config={"displayModeBar": False, "responsive": True}, className="chart-graph"), color=THEME["accent"]),
                        ],
                        className="glass-card chart-card",
                    ),
                ],
                className="graph-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div([html.H3("Anomaly signal", className="chart-title"), html.P("Deviation from the expected monthly baseline.", className="chart-subtitle")], className="chart-head compact"),
                            dcc.Loading(dcc.Graph(id="anomaly-spark", config={"displayModeBar": False, "responsive": True}, className="chart-graph compact"), color=THEME["warning"]),
                        ],
                        className="glass-card chart-card compact-card",
                    ),
                    html.Div(
                        [
                            html.H3("Pipeline throughput", className="chart-title"),
                            html.P("Operational telemetry across the serverless data flow.", className="chart-subtitle"),
                            html.Div(throughput_rows(DATA_META), className="progress-list"),
                        ],
                        className="glass-card chart-card compact-card",
                    ),
                    html.Div(
                        [
                            html.H3("Recent signals", className="chart-title"),
                            html.P("Freshness, mode, and hotspot context for the active view.", className="chart-subtitle"),
                            html.Div(id="event-feed", className="event-feed"),
                        ],
                        className="glass-card chart-card compact-card",
                    ),
                ],
                className="support-grid",
            ),
        ],
        id="dashboard",
        className="section-block",
    )


def build_architecture():
    flow_children = []
    for index, step in enumerate(PIPELINE_STEPS):
        flow_children.append(
            html.Div(
                [
                    html.Div(step["code"], className="arch-code"),
                    html.P(step["label"], className="arch-label"),
                    html.P(step["sub"], className="arch-sub"),
                ],
                className="arch-node",
            )
        )
        if index < len(PIPELINE_STEPS) - 1:
            flow_children.append(html.Div(className="arch-connector"))

    return html.Section(
        [
            html.Div(
                [
                    html.P("Engineering", className="section-kicker"),
                    html.H2("Built on a serverless AWS data pipeline", className="section-title"),
                    html.P("Data source to insight path designed for scalability, resilience, and cost-aware querying.", className="section-copy"),
                ],
                className="section-header solo",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.P("Pipeline architecture", className="panel-kicker"), html.H3("Serverless. Scalable. Cost-efficient.", className="panel-title")]),
                                    html.Div([badge("Serverless", "primary"), badge("Event-driven", "accent"), badge("Fallback-safe", "success")], className="badge-row"),
                                ],
                                className="panel-head architecture-head",
                            ),
                            html.Div(flow_children, className="arch-flow"),
                            html.Div(
                                [
                                    html.Div([html.P("Zero idle compute", className="arch-stat-value"), html.P("Pay only when the pipeline runs", className="arch-stat-label")], className="arch-stat"),
                                    html.Div([html.P("Schema-on-read", className="arch-stat-value"), html.P("Athena and Glue keep analytics agile", className="arch-stat-label")], className="arch-stat"),
                                    html.Div([html.P("Partition-ready", className="arch-stat-value"), html.P("Designed for efficient cloud scans", className="arch-stat-label")], className="arch-stat"),
                                    html.Div([html.P("Resilience mode", className="arch-stat-value"), html.P("Fallback dataset keeps the product live", className="arch-stat-label")], className="arch-stat"),
                                ],
                                className="arch-stats-grid",
                            ),
                        ],
                        className="glass-card architecture-card",
                    )
                ]
            ),
        ],
        id="architecture",
        className="section-block",
    )


def build_highlights():
    feature_cards = []
    for item in FEATURES:
        feature_cards.append(
            html.Div(
                [
                    html.Div(item["code"], className="feature-code"),
                    html.H3(item["title"], className="feature-title"),
                    html.P(item["description"], className="feature-copy"),
                ],
                className="glass-card feature-card",
            )
        )

    return html.Section(
        [
            html.Div(
                [
                    html.P("Engineering highlights", className="section-kicker"),
                    html.H2("Production-grade by design", className="section-title"),
                    html.P("The application experience is backed by cloud architecture choices that favor maintainability, availability, and recruiter-visible technical depth.", className="section-copy"),
                ],
                className="section-header solo",
            ),
            html.Div(feature_cards, className="feature-grid"),
            html.Div(
                [
                    html.P("Stack", className="panel-kicker"),
                    html.Div([html.Span(tag, className="stack-tag") for tag in STACK_TAGS], className="stack-grid"),
                ],
                className="glass-card stack-card",
            ),
        ],
        id="highlights",
        className="section-block",
    )


def build_use_cases():
    cards = []
    for item in USE_CASES:
        cards.append(
            html.Div(
                [
                    html.Div(item["code"], className="use-case-code"),
                    html.H3(item["title"], className="feature-title"),
                    html.P(item["description"], className="feature-copy"),
                ],
                className="glass-card use-case-card",
            )
        )

    return html.Section(
        [
            html.Div(
                [
                    html.P("Use cases", className="section-kicker"),
                    html.H2("Climate intelligence for the people making decisions", className="section-title"),
                    html.P("Position the platform as a practical data product for planning, adaptation, and operational risk response.", className="section-copy"),
                ],
                className="section-header solo",
            ),
            html.Div(cards, className="use-case-grid"),
        ],
        id="use-cases",
        className="section-block",
    )


def build_cta():
    return html.Section(
        [
            html.Div(
                [
                    html.P("Next step", className="section-kicker centered"),
                    html.H2(["Climate decisions deserve ", html.Span("production-grade data", className="text-gradient")], className="cta-title"),
                    html.P("Explore the repository, inspect the architecture, or connect directly for data engineering, cloud, and backend opportunities.", className="cta-copy"),
                    html.Div(
                        [
                            button_link("View GitHub", GITHUB_REPO, variant="primary", external=True),
                            button_link("Explore architecture", "#architecture", variant="secondary"),
                            button_link("Hire Me / Contact", CONTACT_URL, variant="ghost", external=True),
                        ],
                        className="cta-actions",
                    ),
                ],
                className="glass-card cta-card",
            )
        ],
        className="section-block cta-section",
    )


def build_footer():
    return html.Footer(
        [
            html.Div(
                [
                    html.P("AfriClimate Analytics Platform", className="footer-brand"),
                    html.P("Built with Dash, Plotly, Python, and AWS serverless services.", className="footer-copy"),
                ],
                className="footer-copy-block",
            ),
            html.Div(
                [
                    html.Span("System operational", className="footer-meta"),
                    html.Span("Data source: CHIRPS v2.0", className="footer-meta"),
                ],
                className="footer-meta-block",
            ),
        ],
        className="footer-block",
    )


DATAFRAME, DATA_META = load_data()
LOCATION_OPTIONS = [{"label": "All locations", "value": "All locations"}] + [
    {"label": location, "value": location} for location in sorted(DATAFRAME["province"].dropna().unique())
]

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.title = "AfriClimate Analytics Platform"

app.layout = html.Div(
    [
        dcc.Interval(id="clock-tick", interval=1000, n_intervals=0),
        html.Header(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(className="brand-mark"),
                                html.Div(
                                    [
                                        html.P("AfriClimate", className="brand-title"),
                                        html.P("ANALYTICS PLATFORM", className="brand-subtitle"),
                                    ],
                                    className="brand-copy-block",
                                ),
                            ],
                            className="brand-block",
                        ),
                        html.Nav([html.A(label, href=href, className="header-link") for label, href in NAV_LINKS], className="header-nav"),
                        html.Div(
                            [
                                html.Div([html.Span(className="status-ping tone-bg-success"), html.Span(DATA_META["status"], className="header-status-text")], className="status-chip"),
                                button_link("View GitHub", GITHUB_REPO, variant="secondary", external=True),
                            ],
                            className="header-actions",
                        ),
                    ],
                    className="header-inner",
                )
            ],
            className="top-header",
        ),
        html.Div(
            [
                build_sidebar(DATA_META, DATAFRAME),
                html.Main(
                    [
                        build_hero(DATA_META, DATAFRAME),
                        build_dashboard(),
                        build_architecture(),
                        build_highlights(),
                        build_use_cases(),
                        build_cta(),
                        build_footer(),
                    ],
                    className="page-content",
                ),
            ],
            className="page-frame",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("live-clock", "children"),
    Output("sidebar-clock", "children"),
    Input("clock-tick", "n_intervals"),
)
def update_clock(_):
    now = datetime.now(SAST)
    return now.strftime("%H:%M:%S SAST"), now.strftime("%d %b %Y, %H:%M")


@app.callback(
    Output("metric-rainfall-value", "children"),
    Output("metric-rainfall-detail", "children"),
    Output("metric-anomaly-value", "children"),
    Output("metric-anomaly-detail", "children"),
    Output("metric-alerts-value", "children"),
    Output("metric-alerts-detail", "children"),
    Output("metric-coverage-value", "children"),
    Output("metric-coverage-detail", "children"),
    Output("trend-badge", "children"),
    Output("trend-insight", "children"),
    Output("rainfall-trend", "figure"),
    Output("regional-bars", "figure"),
    Output("anomaly-spark", "figure"),
    Output("event-feed", "children"),
    Input("location-filter", "value"),
    Input("window-filter", "value"),
    Input("condition-filter", "value"),
)
def update_dashboard(location, window, condition):
    filtered = apply_filters(DATAFRAME, location, window, condition)
    reference = comparison_slice(DATAFRAME, location)

    if filtered.empty:
        empty_events = [
            event_item("Source", DATA_META["mode"], DATA_META["source"], tone="accent"),
            event_item("Filters", "No matching records", f"{WINDOW_LABELS.get(window, window)} and {CONDITION_LABELS.get(condition, condition)} returned no visible observations.", tone="warning"),
        ]
        return (
            "0.0 mm",
            "No rainfall records in this slice",
            "0.00 sigma",
            "No anomaly context available",
            "0",
            "No drought alerts in this slice",
            f"0 / {DATAFRAME['province'].nunique()}",
            "No visible areas",
            "No visible data",
            "No records match the selected location, time window, and condition filters.",
            empty_figure("No rainfall records match the selected filters.", 320),
            empty_figure("No regional comparison is available for the selected slice.", 320),
            empty_figure("No anomaly signal is available for the selected slice.", 120),
            empty_events,
        )

    mean_rainfall = float(filtered["precipitation"].mean())
    reference_mean = float(reference["precipitation"].mean()) if not reference.empty else mean_rainfall
    rainfall_delta = safe_pct_delta(mean_rainfall, reference_mean)

    anomaly_index = float(filtered["anomaly_sigma"].mean())
    severe_alerts = int(filtered["drought_level"].isin(["Severe", "Extreme"]).sum())
    extreme_alerts = int((filtered["drought_level"] == "Extreme").sum())
    visible_areas = int(filtered["province"].nunique())
    total_areas = int(DATAFRAME["province"].nunique())

    province_summary = (
        filtered.groupby("province", as_index=False)
        .agg(precipitation=("precipitation", "mean"), climate_risk=("climate_risk", "mean"))
        .sort_values("precipitation", ascending=True)
    )
    driest_area = province_summary.iloc[0]["province"]
    driest_rainfall = float(province_summary.iloc[0]["precipitation"])
    driest_risk = float(province_summary.iloc[0]["climate_risk"])

    reference_by_area = reference.groupby("province")["precipitation"].mean()
    driest_baseline = float(reference_by_area.get(driest_area, reference_mean))
    driest_delta = safe_pct_delta(driest_rainfall, driest_baseline)
    delta_direction = "below" if driest_delta < 0 else "above"

    insight = (
        f"{driest_area} is the driest visible area, running {abs(driest_delta):.1f}% {delta_direction} its baseline "
        f"with a climate risk score of {driest_risk:.0f}/100."
    )
    badge_text = f"{signed_text(rainfall_delta, '%')} vs baseline"

    event_feed = [
        event_item("Source", DATA_META["mode"], DATA_META["source"], tone="accent"),
        event_item("Window", WINDOW_LABELS.get(window, window), f"{len(filtered):,} observations across {visible_areas} visible areas.", tone="success"),
        event_item("Hotspot", driest_area, f"{abs(driest_delta):.1f}% {delta_direction} baseline rainfall and {driest_risk:.0f}/100 risk.", tone="warning"),
    ]

    return (
        f"{mean_rainfall:.1f} mm",
        f"{signed_text(rainfall_delta, '%')} versus location baseline",
        f"{signed_text(anomaly_index, ' sigma', decimals=2)}",
        "Positive values indicate wetter conditions; negative values indicate dryness pressure.",
        str(severe_alerts),
        f"{extreme_alerts} critical records flagged as extreme",
        f"{visible_areas} / {total_areas}",
        "Areas represented in the active analytical slice",
        badge_text,
        insight,
        build_rainfall_figure(filtered, reference),
        build_region_figure(filtered),
        build_anomaly_figure(filtered, reference),
        event_feed,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("DASH_DEBUG_MODE", "False").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    app.run(debug=debug, host=host, port=port)
