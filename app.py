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

CARD_ORDER = ["drought", "water", "climate", "community", "carbon"]
ACCENT = {
    "drought": "#ef4444",
    "water": "#2563eb",
    "climate": "#10b981",
    "community": "#f59e0b",
    "carbon": "#f97316",
}
TITLES = {
    "drought": "Drought Analysis",
    "water": "Water Security",
    "climate": "Climate Risk",
    "community": "Community Impact",
    "carbon": "Carbon Emissions",
}


def build_fallback_data():
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
    for year in [2021, 2022, 2023, 2024]:
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
    out = df.copy()
    out["year_month"] = out["year"].astype(str) + "-" + out["month"].astype(str).str.zfill(2)
    out["season"] = out["month"].apply(lambda m: "Summer" if m in [12, 1, 2] else "Autumn" if m in [3, 4, 5] else "Winter" if m in [6, 7, 8] else "Spring")
    out["drought_level"] = out["precipitation"].apply(lambda x: "Low" if x > 75 else "Moderate" if x > 50 else "Severe" if x > 25 else "Extreme")
    out["climate_risk"] = out.apply(
        lambda r: (r["precipitation"] < 50) * 0.3 + (r["drought_level"] in ["Severe", "Extreme"]) * 0.4 + (r["season"] == "Summer") * 0.2 + (abs(r["latitude"]) > 30) * 0.1,
        axis=1,
    )
    out["date"] = pd.to_datetime(out[["year", "month", "day"]], errors="coerce")
    out["carbon_emissions"] = np.random.uniform(50, 200, len(out))
    out["community_impact"] = np.random.randint(1, 100, len(out))
    return out


def load_data():
    if os.getenv("FORCE_FALLBACK_DATA", "true").lower() == "true":
        print("FORCE_FALLBACK_DATA=true; using local fallback data.")
        return enrich_dataframe(build_fallback_data())
    if wr is None:
        return enrich_dataframe(build_fallback_data())
    boto3.setup_default_session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "af-south-1"),
    )
    try:
        q = """
        SELECT latitude, longitude, precipitation, year, month, day
        FROM africlimate_climate_db.chirps_data
        WHERE year BETWEEN 2020 AND 2024
        LIMIT 3000
        """
        data = wr.athena.read_sql_query(
            sql=q,
            database="africlimate_climate_db",
            workgroup="primary",
            s3_output="s3://aws-athena-query-results-701742813629-af-south-1/",
        )
        if data.empty:
            return enrich_dataframe(build_fallback_data())
        return enrich_dataframe(data)
    except Exception as exc:
        print(f"ATHENA LOAD ERROR: {exc}")
        return enrich_dataframe(build_fallback_data())


def card_style(color, mode="normal"):
    style = {
        "background": "linear-gradient(145deg, rgba(255,255,255,0.92), rgba(241,245,255,0.92))",
        "border": f"1px solid {color}55",
        "borderTop": f"4px solid {color}",
        "borderRadius": "18px",
        "padding": "1rem",
        "boxShadow": "0 10px 28px rgba(15,23,42,0.11)",
        "transition": "all 0.35s ease",
        "position": "relative",
        "zIndex": "2",
    }
    if mode == "focus":
        style.update(
            {
                "position": "fixed",
                "left": "50%",
                "top": "52%",
                "transform": "translate(-50%, -50%) scale(1.04)",
                "width": "min(94vw, 980px)",
                "maxHeight": "86vh",
                "overflowY": "auto",
                "zIndex": "1200",
                "boxShadow": "0 20px 55px rgba(15,23,42,0.34)",
            }
        )
    if mode == "dim":
        style.update({"opacity": "0.2", "transform": "scale(0.96)", "filter": "blur(1px)", "pointerEvents": "none"})
    return style


def overlay_style(show):
    return {
        "position": "fixed",
        "inset": "0",
        "background": "rgba(2,6,23,0.46)",
        "backdropFilter": "blur(2px)",
        "zIndex": "900",
        "display": "block" if show else "none",
    }


def mk_card(key):
    return html.Div(
        [
            html.H3(TITLES[key], style={"margin": "0", "fontSize": "1.2rem", "color": ACCENT[key]}),
            html.P(id=f"{key}-metric", style={"margin": "8px 0 0", "fontWeight": "700"}),
            dcc.Graph(id=f"{key}-chart", config={"displayModeBar": False}),
        ],
        id=f"card-{key}",
        style=card_style(ACCENT[key]),
    )


def styled_figure(fig, title, height):
    fig.update_layout(
        template="plotly_white",
        title={"text": title, "font": {"size": 16, "color": "#0f172a"}},
        height=height,
        margin={"l": 28, "r": 16, "t": 55, "b": 28},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Poppins, Segoe UI, sans-serif", "color": "#0f172a"},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def empty_figure(title):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", title=title, height=320)
    return fig


def hotspot(series, low=False):
    if series.empty:
        return "no province"
    return str(series.idxmin() if low else series.idxmax())


df = load_data()
print(f"Loaded rows: {len(df)}")

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "AfriClimate Analytics Platform"

app.layout = html.Div(
    [
        html.Div(id="focus-overlay", style=overlay_style(False)),
        html.Div(
            [
                html.H1("AfriClimate Climate Intelligence Dashboard", style={"margin": "0", "fontSize": "2.3rem", "fontWeight": "800", "color": "#0b3b84"}),
                html.P("Real-time analytics for drought, water security, climate risk, community impact, and carbon pressure.", style={"margin": "10px 0 0", "fontSize": "1.04rem", "color": "#334155"}),
            ],
            style={"padding": "1.8rem 1.4rem", "maxWidth": "1250px", "margin": "0 auto"},
        ),
        html.Div(
            [
                html.Div(
                    [html.H2("Filter Controls", style={"margin": "0", "fontSize": "1.2rem", "fontWeight": "800", "color": "#0f172a"}), html.P("Filter by Province, Years, and 5 Analysis Modules.", style={"margin": "6px 0 0", "fontSize": "0.95rem", "color": "#475569"})],
                    style={"gridColumn": "1 / -1"},
                ),
                html.Div([html.P("Province", style={"margin": "0 0 8px", "fontWeight": "700", "fontSize": "0.85rem"}), dcc.Dropdown(id="province-filter", options=[{"label": "All", "value": "All"}] + [{"label": p, "value": p} for p in sorted(df["province"].dropna().unique())], value="All", clearable=False)]),
                html.Div([html.P("Years", style={"margin": "0 0 8px", "fontWeight": "700", "fontSize": "0.85rem"}), dcc.Dropdown(id="year-filter", options=[{"label": "All", "value": "All"}] + [{"label": str(y), "value": int(y)} for y in sorted(df["year"].dropna().astype(int).unique())], value="All", clearable=False)]),
                html.Div([html.P("5 Analysis Modules", style={"margin": "0 0 8px", "fontWeight": "700", "fontSize": "0.85rem"}), dcc.Dropdown(id="analysis-type", options=[{"label": "All", "value": "All"}, {"label": "Drought Analysis", "value": "drought"}, {"label": "Water Security", "value": "water"}, {"label": "Climate Risk", "value": "climate"}, {"label": "Community Impact", "value": "community"}, {"label": "Carbon Emissions", "value": "carbon"}], value="All", clearable=False)]),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(230px, 1fr))", "gap": "1rem", "padding": "1.15rem", "maxWidth": "1250px", "margin": "0 auto", "background": "linear-gradient(135deg, rgba(255,255,255,0.85), rgba(241,245,255,0.92))", "border": "1px solid #cbd5e1", "borderRadius": "18px", "boxShadow": "0 12px 28px rgba(15, 23, 42, 0.1)"},
        ),
        html.Div([mk_card("drought"), mk_card("water"), mk_card("climate"), mk_card("community"), mk_card("carbon")], id="dashboard-grid", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(340px, 1fr))", "gap": "1.15rem", "padding": "1rem 0 0.4rem", "maxWidth": "1250px", "margin": "1rem auto 0"}),
        html.Div(
            [
                html.H3("Provincial Effect Highlights", style={"margin": "0 0 12px", "fontSize": "1.08rem", "fontWeight": "800", "color": "#0f172a"}),
                html.Div(
                    [
                        html.Div([html.P("Drought", style={"margin": "0", "fontWeight": "700", "color": ACCENT["drought"]}), html.P(id="insight-drought", style={"margin": "6px 0 0", "fontSize": "0.92rem", "color": "#334155"})], style={"background": "rgba(255,255,255,0.86)", "padding": "0.8rem", "borderRadius": "12px", "border": "1px solid #fecaca"}),
                        html.Div([html.P("Water", style={"margin": "0", "fontWeight": "700", "color": ACCENT["water"]}), html.P(id="insight-water", style={"margin": "6px 0 0", "fontSize": "0.92rem", "color": "#334155"})], style={"background": "rgba(255,255,255,0.86)", "padding": "0.8rem", "borderRadius": "12px", "border": "1px solid #bfdbfe"}),
                        html.Div([html.P("Climate", style={"margin": "0", "fontWeight": "700", "color": ACCENT["climate"]}), html.P(id="insight-climate", style={"margin": "6px 0 0", "fontSize": "0.92rem", "color": "#334155"})], style={"background": "rgba(255,255,255,0.86)", "padding": "0.8rem", "borderRadius": "12px", "border": "1px solid #a7f3d0"}),
                        html.Div([html.P("Community", style={"margin": "0", "fontWeight": "700", "color": ACCENT["community"]}), html.P(id="insight-community", style={"margin": "6px 0 0", "fontSize": "0.92rem", "color": "#334155"})], style={"background": "rgba(255,255,255,0.86)", "padding": "0.8rem", "borderRadius": "12px", "border": "1px solid #fde68a"}),
                        html.Div([html.P("Carbon", style={"margin": "0", "fontWeight": "700", "color": ACCENT["carbon"]}), html.P(id="insight-carbon", style={"margin": "6px 0 0", "fontSize": "0.92rem", "color": "#334155"})], style={"background": "rgba(255,255,255,0.86)", "padding": "0.8rem", "borderRadius": "12px", "border": "1px solid #fed7aa"}),
                    ],
                    style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(210px, 1fr))", "gap": "0.7rem"},
                ),
            ],
            style={"maxWidth": "1250px", "margin": "0.4rem auto 2rem", "padding": "1rem", "background": "linear-gradient(135deg, rgba(255,255,255,0.87), rgba(240,249,255,0.9))", "borderRadius": "16px", "border": "1px solid #cbd5e1", "boxShadow": "0 8px 22px rgba(15, 23, 42, 0.1)"},
        ),
    ],
    style={"minHeight": "100vh", "padding": "0 1rem", "background": "radial-gradient(circle at 10% 12%, #dbeafe 0%, #eff6ff 28%, #f8fafc 62%, #f1f5f9 100%)", "fontFamily": "Poppins, Segoe UI, sans-serif"},
)


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
        Output("card-drought", "style"),
        Output("card-water", "style"),
        Output("card-climate", "style"),
        Output("card-community", "style"),
        Output("card-carbon", "style"),
        Output("focus-overlay", "style"),
        Output("insight-drought", "children"),
        Output("insight-water", "children"),
        Output("insight-climate", "children"),
        Output("insight-community", "children"),
        Output("insight-carbon", "children"),
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

    focus = analysis_type if analysis_type in CARD_ORDER else None
    heights = {k: 500 if focus == k else 260 if focus else 320 for k in CARD_ORDER}

    styles = [card_style(ACCENT[k], "focus" if focus == k else "dim" if focus else "normal") for k in CARD_ORDER]

    if filtered.empty:
        empty = empty_figure("No data for current filters")
        return (
            empty,
            empty,
            empty,
            empty,
            empty,
            "No drought records in this filter.",
            "No rainfall records in this filter.",
            "No climate risk records in this filter.",
            "No community records in this filter.",
            "No carbon records in this filter.",
            styles[0],
            styles[1],
            styles[2],
            styles[3],
            styles[4],
            overlay_style(bool(focus)),
            "Drought impact cannot be assessed because no province data is available.",
            "Water pressure cannot be assessed because no province data is available.",
            "Climate risk cannot be assessed because no province data is available.",
            "Community impact cannot be assessed because no province data is available.",
            "Carbon impact cannot be assessed because no province data is available.",
        )

    drought_counts = filtered["drought_level"].value_counts().reindex(["Low", "Moderate", "Severe", "Extreme"], fill_value=0)
    drought_fig = styled_figure(go.Figure(go.Bar(x=drought_counts.index, y=drought_counts.values, marker_color=ACCENT["drought"])), "Drought Severity Distribution", heights["drought"])
    water = filtered.groupby("month", as_index=False)["precipitation"].mean().sort_values("month")
    water_fig = styled_figure(go.Figure(go.Scatter(x=water["month"], y=water["precipitation"], mode="lines+markers", line={"color": ACCENT["water"], "width": 3}, marker={"size": 8})), "Average Monthly Rainfall (mm)", heights["water"])
    climate = filtered.groupby("month", as_index=False)["climate_risk"].mean().sort_values("month")
    climate_fig = styled_figure(go.Figure(go.Scatter(x=climate["month"], y=climate["climate_risk"], mode="lines+markers", line={"color": ACCENT["climate"], "width": 3}, marker={"size": 8})), "Climate Risk Trend", heights["climate"])
    community = filtered.groupby("province", as_index=False)["community_impact"].mean().sort_values("community_impact", ascending=False)
    community_fig = styled_figure(go.Figure(go.Bar(x=community["province"], y=community["community_impact"], marker_color=ACCENT["community"])), "Community Impact by Province", heights["community"])
    carbon = filtered.groupby("province", as_index=False)["carbon_emissions"].mean().sort_values("carbon_emissions", ascending=False)
    carbon_fig = styled_figure(go.Figure(go.Bar(x=carbon["province"], y=carbon["carbon_emissions"], marker_color=ACCENT["carbon"])), "Average Carbon Emissions", heights["carbon"])

    drought_metric = f"{int((filtered['drought_level'].isin(['Severe', 'Extreme'])).sum())} severe or extreme records"
    water_metric = f"{filtered['precipitation'].mean():.1f} mm average rainfall"
    climate_metric = f"{filtered['climate_risk'].mean():.2f} average climate risk"
    community_metric = f"{filtered['community_impact'].mean():.0f} average community impact score"
    carbon_metric = f"{filtered['carbon_emissions'].mean():.1f} average carbon emissions"

    drought_hotspot = hotspot(filtered.assign(severe=filtered["drought_level"].isin(["Severe", "Extreme"])).groupby("province")["severe"].mean())
    water_hotspot = hotspot(filtered.groupby("province")["precipitation"].mean(), low=True)
    climate_hotspot = hotspot(filtered.groupby("province")["climate_risk"].mean())
    community_hotspot = hotspot(filtered.groupby("province")["community_impact"].mean())
    carbon_hotspot = hotspot(filtered.groupby("province")["carbon_emissions"].mean())

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
        styles[0],
        styles[1],
        styles[2],
        styles[3],
        styles[4],
        overlay_style(bool(focus)),
        f"Drought pressure is currently strongest in {drought_hotspot} based on severe and extreme events.",
        f"Water security strain appears highest in {water_hotspot} because it has the lowest average rainfall.",
        f"Climate risk concentration is highest in {climate_hotspot} under the selected filters.",
        f"Community impact intensity peaks in {community_hotspot} from the current impact index.",
        f"Carbon emissions are most elevated in {carbon_hotspot} compared with other visible provinces.",
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("DASH_DEBUG_MODE", "False").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    app.run(debug=debug, host=host, port=port)
