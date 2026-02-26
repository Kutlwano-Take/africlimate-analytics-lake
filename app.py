import os

import boto3
import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from dotenv import load_dotenv

try:
    import awswrangler as wr
except Exception:
    wr = None

load_dotenv()


def build_fallback_data():
    """Create a local dataset so the app always starts."""
    rng = np.random.default_rng(42)
    provinces = [
        "Gauteng",
        "Limpopo",
        "Mpumalanga",
        "KwaZulu-Natal",
        "Eastern Cape",
        "Western Cape",
        "Northern Cape",
        "North West",
        "Free State",
    ]

    rows = []
    for year in [2022, 2023]:
        for month in [1, 4, 7, 10]:
            for province in provinces:
                rows.append(
                    {
                        "latitude": float(rng.uniform(-34, -22)),
                        "longitude": float(rng.uniform(18, 33)),
                        "precipitation": float(rng.uniform(5, 120)),
                        "year": year,
                        "month": month,
                        "day": int(rng.integers(1, 28)),
                        "province": province,
                    }
                )
    return pd.DataFrame(rows)


def enrich_dataframe(df):
    df = df.copy()

    if "province" not in df.columns:
        df["province"] = df.apply(
            lambda row: (
                "Gauteng"
                if -27 <= row["latitude"] <= -25 and 27 <= row["longitude"] <= 29
                else (
                    "Limpopo"
                    if -24 <= row["latitude"] <= -22 and 28 <= row["longitude"] <= 32
                    else (
                        "Mpumalanga"
                        if -26 <= row["latitude"] <= -24 and 29 <= row["longitude"] <= 32
                        else (
                            "KwaZulu-Natal"
                            if -30 <= row["latitude"] <= -27 and 29 <= row["longitude"] <= 33
                            else (
                                "Eastern Cape"
                                if -31 <= row["latitude"] <= -28 and 23 <= row["longitude"] <= 30
                                else (
                                    "Western Cape"
                                    if -34 <= row["latitude"] <= -31 and 18 <= row["longitude"] <= 23
                                    else (
                                        "Northern Cape"
                                        if -32 <= row["latitude"] <= -28 and 18 <= row["longitude"] <= 24
                                        else (
                                            "North West"
                                            if -27 <= row["latitude"] <= -25 and 22 <= row["longitude"] <= 27
                                            else (
                                                "Free State"
                                                if -30 <= row["latitude"] <= -26 and 24 <= row["longitude"] <= 29
                                                else "Southern Africa Region"
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            axis=1,
        )

    df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    df["season"] = df["month"].apply(
        lambda x: "Summer" if x in [12, 1, 2] else "Autumn" if x in [3, 4, 5] else "Winter" if x in [6, 7, 8] else "Spring"
    )
    df["drought_level"] = df["precipitation"].apply(
        lambda x: "Low" if x > 75 else "Moderate" if x > 50 else "Severe" if x > 25 else "Extreme"
    )
    df["climate_risk"] = df.apply(
        lambda row: (
            (row["precipitation"] < 50) * 0.3
            + (row["drought_level"] in ["Severe", "Extreme"]) * 0.4
            + (row["season"] == "Summer") * 0.2
            + (abs(row["latitude"]) > 30) * 0.1
        ),
        axis=1,
    )
    df["date"] = pd.to_datetime(df[["year", "month", "day"]], errors="coerce")
    df["carbon_emissions"] = np.random.uniform(50, 200, len(df))
    df["community_impact"] = np.random.randint(1, 100, len(df))
    return df


def load_data():
    # Default to fallback so the dashboard always shows data immediately.
    force_fallback = os.getenv("FORCE_FALLBACK_DATA", "true").lower() == "true"
    if force_fallback:
        print("FORCE_FALLBACK_DATA=true; using local fallback data.")
        return enrich_dataframe(build_fallback_data())

    if wr is None:
        print("awswrangler unavailable; using fallback data.")
        return enrich_dataframe(build_fallback_data())

    boto3.setup_default_session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "af-south-1"),
    )

    try:
        query = """
        SELECT latitude, longitude, precipitation, year, month, day
        FROM africlimate_climate_db.chirps_data
        WHERE year BETWEEN 2020 AND 2023
        LIMIT 3000
        """
        print("Executing Athena query...")
        df = wr.athena.read_sql_query(
            sql=query,
            database="africlimate_climate_db",
            workgroup="primary",
            s3_output="s3://aws-athena-query-results-701742813629-af-south-1/",
        )
        if df.empty:
            print("Athena returned 0 rows; using fallback data.")
            return enrich_dataframe(build_fallback_data())
        return enrich_dataframe(df)
    except Exception as exc:
        print(f"ATHENA LOAD ERROR: {exc}")
        return enrich_dataframe(build_fallback_data())


df = load_data()
print(f"Loaded rows: {len(df)}")

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "AfriClimate Analytics Platform"
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "AfriClimate Analytics Platform",
                    style={"textAlign": "center", "margin": "0", "fontSize": "2.2rem", "color": "#1e40af"},
                ),
                html.P(
                    "Advanced Climate Intelligence for Southern Africa",
                    style={"textAlign": "center", "margin": "8px 0 0", "color": "#4b5563"},
                ),
            ],
            style={"padding": "1.5rem", "background": "#f0f9ff", "borderBottom": "1px solid #bfdbfe"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="province-filter",
                    options=[{"label": "All", "value": "All"}]
                    + [{"label": p, "value": p} for p in sorted(df["province"].dropna().unique())],
                    value="All",
                ),
                dcc.Dropdown(
                    id="year-filter",
                    options=[{"label": "All", "value": "All"}]
                    + [{"label": str(y), "value": int(y)} for y in sorted(df["year"].dropna().astype(int).unique())],
                    value="All",
                ),
                dcc.Dropdown(
                    id="analysis-type",
                    options=[
                        {"label": "All", "value": "All"},
                        {"label": "Drought Analysis", "value": "drought"},
                        {"label": "Water Security", "value": "water"},
                        {"label": "Climate Risk", "value": "climate"},
                        {"label": "Community Impact", "value": "community"},
                        {"label": "Carbon Footprint", "value": "carbon"},
                    ],
                    value="All",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                "gap": "1rem",
                "padding": "1rem",
                "maxWidth": "1200px",
                "margin": "0 auto",
            },
        ),
        html.Div(
            [
                html.Div([html.P(id="drought-metric"), dcc.Graph(id="drought-chart")]),
                html.Div([html.P(id="water-metric"), dcc.Graph(id="water-chart")]),
                html.Div([html.P(id="climate-metric"), dcc.Graph(id="climate-chart")]),
                html.Div([html.P(id="community-metric"), dcc.Graph(id="community-chart")]),
                html.Div([html.P(id="carbon-metric"), dcc.Graph(id="carbon-chart")]),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(340px, 1fr))",
                "gap": "1rem",
                "padding": "1rem",
            },
        ),
    ],
    style={"background": "#f8fafc", "minHeight": "100vh"},
)


def _empty_figure(title):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", title=title, height=300)
    return fig


@app.callback(
    [
        Output("drought-chart", "figure"),
        Output("water-chart", "figure"),
        Output("climate-chart", "figure"),
        Output("community-chart", "figure"),
        Output("carbon-chart", "figure"),
        Output("drought-metric", "children"),
        Output("water-metric", "children"),
        Output("climate-metric", "children"),
        Output("community-metric", "children"),
        Output("carbon-metric", "children"),
    ],
    [Input("province-filter", "value"), Input("year-filter", "value"), Input("analysis-type", "value")],
)
def update_charts(province, year, analysis_type):
    print("=== UPDATE_CHARTS FIRED ===")
    filtered = df.copy()

    if province and province != "All":
        filtered = filtered[filtered["province"] == province]
    if year and year != "All":
        filtered = filtered[filtered["year"] == int(year)]

    if filtered.empty:
        empty = _empty_figure("No data for current filters")
        return (
            empty,
            empty,
            empty,
            empty,
            empty,
            "0 regions at risk",
            "0.0 mm avg rainfall",
            "0.00 climate risk",
            "0 avg impact",
            "0.0 avg emissions",
        )

    drought_counts = filtered["drought_level"].value_counts().reindex(["Low", "Moderate", "Severe", "Extreme"], fill_value=0)
    drought_fig = go.Figure(go.Bar(x=drought_counts.index, y=drought_counts.values, marker_color="#dc2626"))
    drought_fig.update_layout(template="plotly_white", title="Drought Severity Distribution", height=300)

    water = filtered.groupby("month", as_index=False)["precipitation"].mean().sort_values("month")
    water_fig = go.Figure(go.Scatter(x=water["month"], y=water["precipitation"], mode="lines+markers", line={"color": "#2563eb"}))
    water_fig.update_layout(template="plotly_white", title="Average Monthly Rainfall (mm)", height=300)

    climate = filtered.groupby("month", as_index=False)["climate_risk"].mean().sort_values("month")
    climate_fig = go.Figure(go.Scatter(x=climate["month"], y=climate["climate_risk"], mode="lines+markers", line={"color": "#059669"}))
    climate_fig.update_layout(template="plotly_white", title="Climate Risk Trend", height=300)

    community = filtered.groupby("province", as_index=False)["community_impact"].mean().sort_values("community_impact", ascending=False)
    community_fig = go.Figure(go.Bar(x=community["province"], y=community["community_impact"], marker_color="#7c3aed"))
    community_fig.update_layout(template="plotly_white", title="Community Impact by Province", height=300)

    carbon = filtered.groupby("province", as_index=False)["carbon_emissions"].mean().sort_values("carbon_emissions", ascending=False)
    carbon_fig = go.Figure(go.Bar(x=carbon["province"], y=carbon["carbon_emissions"], marker_color="#ea580c"))
    carbon_fig.update_layout(template="plotly_white", title="Average Carbon Emissions", height=300)

    drought_metric = f"{int((filtered['drought_level'].isin(['Severe', 'Extreme'])).sum())} records at severe risk"
    water_metric = f"{filtered['precipitation'].mean():.1f} mm avg rainfall"
    climate_metric = f"{filtered['climate_risk'].mean():.2f} climate risk index"
    community_metric = f"{filtered['community_impact'].mean():.0f} avg impact score"
    carbon_metric = f"{filtered['carbon_emissions'].mean():.1f} avg emissions"

    return (
        drought_fig,
        water_fig,
        climate_fig,
        community_fig,
        carbon_fig,
        drought_metric,
        water_metric,
        climate_metric,
        community_metric,
        carbon_metric,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("DASH_DEBUG_MODE", "False").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    app.run(debug=debug, host=host, port=port)
