import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import awswrangler as wr
import boto3
import numpy as np
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import dash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =======================================
# Data Loading
# =======================================
def load_data():
    """Load climate data from AWS Athena"""
    # Setup AWS session
    boto3.setup_default_session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'af-south-1')
    )
    
    try:
        # Query data from Athena
        query = '''
        SELECT latitude, longitude, precipitation, year, month, day, 
               year_month, date, drought_level, province, season, climate_risk
        FROM africlimate_climate_db.chirps_data
        WHERE year = 2023
        ORDER BY year_month, latitude, longitude
        '''
        
        df = wr.athena.read_sql_query(query, database="africlimate_climate_db")
        print(f"Loaded {len(df)} rows from Athena")
        print(f"Final data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Add province mapping based on coordinates
        df['province'] = df.apply(lambda row: (
            'Gauteng' if -27 <= row['latitude'] <= -25 and 27 <= row['longitude'] <= 29 else
            'Limpopo' if -24 <= row['latitude'] <= -22 and 28 <= row['longitude'] <= 32 else
            'Mpumalanga' if -26 <= row['latitude'] <= -24 and 29 <= row['longitude'] <= 32 else
            'KwaZulu-Natal' if -30 <= row['latitude'] <= -27 and 29 <= row['longitude'] <= 33 else
            'Eastern Cape' if -31 <= row['latitude'] <= -28 and 23 <= row['longitude'] <= 30 else
            'Western Cape' if -34 <= row['latitude'] <= -31 and 18 <= row['longitude'] <= 23 else
            'Northern Cape' if -32 <= row['latitude'] <= -28 and 18 <= row['longitude'] <= 24 else
            'North West' if -27 <= row['latitude'] <= -25 and 22 <= row['longitude'] <= 27 else
            'Free State' if -30 <= row['latitude'] <= -26 and 24 <= row['longitude'] <= 29 else
            'Southern Africa Region'
        ), axis=1)
        
        # Add seasonal analysis
        df['season'] = df['month'].apply(lambda x: 
            'Summer' if x in [12, 1, 2] else
            'Autumn' if x in [3, 4, 5] else
            'Winter' if x in [6, 7, 8] else 'Spring'
        )
        
        # Add climate risk index
        df['climate_risk'] = df.apply(lambda row: (
            (row['precipitation'] < 50) * 0.3 +  # Low precipitation risk
            (row['drought_level'] in ['Severe', 'Extreme']) * 0.4 +  # Drought severity risk
            (row['season'] == 'Summer') * 0.2 +  # Summer heat stress
            (abs(row['latitude']) > 30) * 0.1  # Geographic extremity risk
        ), axis=1)
        
        print(f"Provinces: {df['province'].unique()}")
        print(f"Years: {df['year'].unique()}")
        return df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return sample data if Athena fails
        return pd.DataFrame({
            'latitude': [-26, -28, -30, -25, -33, -34, -29, -31, -32],
            'longitude': [28, 26, 29, 25, 30, 23, 24, 22, 27],
            'precipitation': [45, 78, 12, 89, 156, 23, 67, 34, 45],
            'year': [2023] * 9,
            'month': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            'day': [15, 30, 15, 30, 15, 30, 15, 30, 15],
            'year_month': ['2023-01', '2023-01', '2023-02', '2023-02', '2023-03', '2023-03', '2023-04', '2023-04', '2023-05'],
            'date': pd.to_datetime(['2023-01-15', '2023-01-30', '2023-02-15', '2023-02-28', '2023-03-15', '2023-03-31', '2023-04-15', '2023-04-30', '2023-05-15']),
            'drought_level': ['Moderate', 'Low', 'Moderate', 'Low', 'Moderate', 'Severe', 'Low', 'Moderate', 'Extreme'],
            'province': ['Gauteng', 'Limpopo', 'Mpumalanga', 'KwaZulu-Natal', 'Eastern Cape', 'Western Cape', 'Northern Cape', 'North West', 'Free State'],
            'season': ['Summer', 'Summer', 'Autumn', 'Autumn', 'Autumn', 'Winter', 'Winter', 'Winter', 'Spring'],
            'climate_risk': [0.3, 0.4, 0.5, 0.2, 0.6, 0.1, 0.7, 0.8, 0.4]
        })
df = load_data()

# =======================================
# Dash App
# =======================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # 1. Header (sticky when scrolling)
    html.Div([
        html.H1("AfriClimate Analytics Platform", 
                style={'textAlign': 'center', 'margin': '0', 'fontSize': '2.4rem', 'color': '#1e40af'}),
        html.P("Advanced Climate Intelligence for Southern Africa | Real-time Insights",
               style={'textAlign': 'center', 'margin': '8px 0 0', 'color': '#4b5563', 'fontSize': '1.1rem'})
    ], style={
        'padding': '2.5rem 2rem 1.5rem',
        'background': 'linear-gradient(135deg, #f0f9ff, #e0f2fe)',
        'borderBottom': '1px solid #bfdbfe',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    }),

    # Sticky Filters (also sticky, below header)
    html.Div([
        html.Div([
            dcc.Dropdown(id='province-filter', placeholder="Select Province", style={'width': '100%', 'maxWidth': '280px'}),
            dcc.Dropdown(id='year-filter', placeholder="Select Year", style={'width': '100%', 'maxWidth': '200px'}),
            dcc.Dropdown(id='analysis-type', placeholder="Analysis Type", style={'width': '100%', 'maxWidth': '300px'})
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
            'gap': '1.25rem',
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '1.5rem 2rem',
            'background': 'rgba(255,255,255,0.92)',
            'backdropFilter': 'blur(12px)',
            'borderBottom': '1px solid #e2e8f0',
            'boxShadow': '0 4px 10px rgba(0,0,0,0.05)',
            'position': 'sticky',
            'top': '140px',
            'zIndex': '999'
        })
    ], style={'background': '#f8fafc'}),

    # Scroll button (floating, appears after scroll)
    html.Button("↓ Explore", id="scroll-to-content", n_clicks=0,
                style={
                    'position': 'fixed',
                    'bottom': '32px',
                    'right': '32px',
                    'zIndex': '1000',
                    'background': '#3b82f6',
                    'color': 'white',
                    'border': 'none',
                    'padding': '14px 28px',
                    'borderRadius': '999px',
                    'fontSize': '1rem',
                    'fontWeight': '600',
                    'cursor': 'pointer',
                    'boxShadow': '0 8px 24px rgba(59,130,246,0.35)',
                    'transition': 'all 0.3s ease',
                    'display': 'none'
                }),

    # Main content with proper spacing (this fixes the big gap)
    html.Div([
        # Cards grid
        html.Div(id='dashboard-cards', children=[
            # Drought Card
            html.Div([
                html.H3("🔴 Drought Alert System", style={'margin': '0', 'fontSize': '1.6rem', 'fontWeight': '700', 'color': '#dc2626'}),
                html.P(id="drought-metric", children="-- Regions at risk", style={'margin': '4px 0 0', 'fontSize': '2.4rem', 'fontWeight': '800', 'color': '#dc2626'}),
                dcc.Graph(id='drought-chart', config={'displayModeBar': False}, style={'height': '320px'})
            ], style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(226,232,240,0.6)',
                'borderRadius': '16px',
                'padding': '1.75rem',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'transition': 'all 0.3s ease'
            }),

            # Water Card
            html.Div([
                html.H3("💧 Water Security Monitor", style={'margin': '0', 'fontSize': '1.6rem', 'fontWeight': '700', 'color': '#2563eb'}),
                html.P(id="water-metric", children="-- Avg rainfall mm", style={'margin': '4px 0 0', 'fontSize': '2.4rem', 'fontWeight': '800', 'color': '#2563eb'}),
                dcc.Graph(id='water-chart', config={'displayModeBar': False}, style={'height': '320px'})
            ], style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(226,232,240,0.6)',
                'borderRadius': '16px',
                'padding': '1.75rem',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'transition': 'all 0.3s ease'
            }),

            # Climate Card
            html.Div([
                html.H3("🌡️ Climate Risk Tracker", style={'margin': '0', 'fontSize': '1.6rem', 'fontWeight': '700', 'color': '#059669'}),
                html.P(id="climate-metric", children="-- Risk index", style={'margin': '4px 0 0', 'fontSize': '2.4rem', 'fontWeight': '800', 'color': '#059669'}),
                dcc.Graph(id='climate-chart', config={'displayModeBar': False}, style={'height': '320px'})
            ], style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(226,232,240,0.6)',
                'borderRadius': '16px',
                'padding': '1.75rem',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'transition': 'all 0.3s ease'
            }),

            # Community Card
            html.Div([
                html.H3("👥 Community Impact", style={'margin': '0', 'fontSize': '1.6rem', 'fontWeight': '700', 'color': '#7c3aed'}),
                html.P(id="community-metric", children="-- Impact score", style={'margin': '4px 0 0', 'fontSize': '2.4rem', 'fontWeight': '800', 'color': '#7c3aed'}),
                dcc.Graph(id='community-chart', config={'displayModeBar': False}, style={'height': '320px'})
            ], style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(226,232,240,0.6)',
                'borderRadius': '16px',
                'padding': '1.75rem',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'transition': 'all 0.3s ease'
            }),

            # Carbon Card
            html.Div([
                html.H3("🌍 Carbon Footprint", style={'margin': '0', 'fontSize': '1.6rem', 'fontWeight': '700', 'color': '#ea580c'}),
                html.P(id="carbon-metric", children="-- Emissions tons", style={'margin': '4px 0 0', 'fontSize': '2.4rem', 'fontWeight': '800', 'color': '#ea580c'}),
                dcc.Graph(id='carbon-chart', config={'displayModeBar': False}, style={'height': '320px'})
            ], style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(226,232,240,0.6)',
                'borderRadius': '16px',
                'padding': '1.75rem',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'transition': 'all 0.3s ease'
            })
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(340px, 1fr))',
            'gap': '1.75rem',
            'padding': '2rem 2rem 4rem',
            'maxWidth': '1440px',
            'margin': '0 auto'
        })
    ], style={
        'paddingTop': '180px',
        'minHeight': 'calc(100vh - 180px)'
    }),

    # JavaScript for smooth scroll and button visibility
    html.Script("""
        window.addEventListener('scroll', function() {
            const btn = document.getElementById('scroll-to-content');
            if (window.scrollY > 250) {
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none';
            }
        });

        document.getElementById('scroll-to-content').addEventListener('click', function() {
            document.querySelector('#dashboard-cards').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    """)
], style={
    'background': '#f8fafc',
    'minHeight': '100vh',
    'fontFamily': "'Inter', system-ui, sans-serif"
})

# =======================================
# Callbacks
# =======================================
@app.callback(
    [Output('drought-chart', 'figure'),
     Output('water-chart', 'figure'),
     Output('climate-chart', 'figure'),
     Output('community-chart', 'figure'),
     Output('carbon-chart', 'figure'),
     Output('drought-metric', 'children'),
     Output('water-metric', 'children'),
     Output('climate-metric', 'children'),
     Output('community-metric', 'children'),
     Output('carbon-metric', 'children')],
    [Input('province-filter', 'value'),
     Input('year-filter', 'value'),
     Input('analysis-type', 'value')]
)
def update_charts(province, year, analysis_type):
    print(f"Updating charts - Province: {province}, Year: {year}, Analysis: {analysis_type}")
    
    filtered = df.copy()
    print(f"Original data shape: {filtered.shape}")

    # Province filter
    if province != 'All':
        filtered = filtered[filtered['province'] == province]
        print(f"After province filter: {filtered.shape}")

    # Year filter
    if year != 'All':
        filtered = filtered[filtered['year'] == year]
        print(f"After year filter: {filtered.shape}")

    # Analysis type filter
    if analysis_type != 'All':
        if analysis_type == 'drought':
            filtered = filtered[filtered['drought_level'].isin(['Moderate', 'Severe', 'Extreme'])]
        elif analysis_type == 'water':
            filtered = filtered[filtered['precipitation'] > 0]
        elif analysis_type == 'climate':
            filtered = filtered[filtered['climate_risk'] > 0.5]
        elif analysis_type == 'community':
            filtered = filtered[filtered['province'] != 'Southern Africa Region']
        elif analysis_type == 'carbon':
            filtered = filtered.copy()
            filtered['carbon_emissions'] = np.random.uniform(50, 200, len(filtered))
        print(f"After analysis filter: {filtered.shape}")

    # Create charts
    drought_fig = px.scatter(filtered, x='longitude', y='latitude', color='precipitation',
                             title='🔴 Drought Alert System', 
                             color_continuous_scale='Reds',
                             labels={'precipitation': 'Precipitation (mm)', 'province': 'Province'},
                             hover_data=['precipitation', 'province', 'date'])
    
    water_fig = px.bar(filtered.groupby('province')['precipitation'].mean().reset_index(),
                     x='province', y='precipitation',
                     title='💧 Water Security Monitor',
                     labels={'precipitation': 'Average Precipitation (mm)', 'province': 'Province'},
                     color='province')
    
    climate_fig = px.scatter(filtered, x='precipitation', y='climate_risk',
                           title='🌡️ Climate Risk Tracker',
                           color='climate_risk',
                           color_continuous_scale='RdYlGn',
                           labels={'climate_risk': 'Risk Index', 'province': 'Province'},
                           hover_data=['climate_risk', 'province', 'season'])
    
    carbon_fig = px.bar(filtered, x='province', y='carbon_emissions' if 'carbon_emissions' in filtered.columns else 0,
                     title='🌍 Carbon Footprint',
                     labels={'carbon_emissions': 'Carbon Emissions (tons)', 'province': 'Province'},
                     color='province')

    # Update metrics
    drought_regions = len(filtered[filtered['drought_level'].isin(['Moderate', 'Severe', 'Extreme'])]['province'].unique())
    water_avg = filtered['precipitation'].mean()
    climate_risk_avg = filtered['climate_risk'].mean()
    community_score = len(filtered[filtered['province'] != 'Southern Africa Region'])
    carbon_total = filtered['carbon_emissions'].sum() if 'carbon_emissions' in filtered.columns else 0

    return (
        drought_fig,
        water_fig,
        climate_fig,
        community_fig,
        carbon_fig,
        f"{drought_regions} regions at risk",
        f"{water_avg:.1f} avg rainfall mm",
        f"{climate_risk_avg:.2f} risk index",
        f"{community_score} impact score",
        f"{carbon_total:.0f} emissions tons"
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    debug = os.getenv('DASH_DEBUG_MODE', 'False').lower() == 'true'
    host = os.getenv('DASH_HOST', '0.0.0.0')
    app.run_server(debug=debug, host=host, port=port)
