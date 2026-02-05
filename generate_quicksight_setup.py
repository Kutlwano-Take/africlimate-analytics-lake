#!/usr/bin/env python3
"""
QuickSight Dashboard SQL Queries Generator
Creates all SQL queries needed for the AfriClimate Analytics Lake dashboard
"""

import json
from datetime import datetime

# SQL Queries for QuickSight Datasets
QUICKSIGHT_QUERIES = {
    'drought_early_warning': '''
-- Drought Early Warning Dataset
SELECT 
    year,
    month,
    province,
    region,
    drought_level,
    risk_level,
    monthly_precip,
    avg_spi,
    farmer_message,
    analysis_date
FROM africlimate_climate_db.drought_alerts
ORDER BY analysis_date DESC
    ''',
    
    'water_security': '''
-- Water Security Dataset
SELECT 
    dam_name,
    province,
    current_capacity_percent,
    rainfall_status,
    overall_security_score,
    risk_level,
    days_until_critical,
    recommendations,
    analysis_date
FROM africlimate_climate_db.water_security_metrics
ORDER BY analysis_date DESC
    ''',
    
    'ndvi_impact_tracker': '''
-- NDVI Impact Tracker Dataset
SELECT 
    area_name,
    ecosystem,
    overall_metrics,
    risk_level,
    biodiversity_impact,
    key_threats,
    recommendations,
    assessment_date
FROM africlimate_climate_db.biodiversity_risk_assessments
ORDER BY assessment_date DESC
    ''',
    
    'community_adaptation': '''
-- Community Adaptation Dataset
SELECT 
    settlement_name,
    population,
    overall_risk_level,
    primary_risks,
    requires_immediate_action,
    vulnerability_factors,
    assessment_date
FROM africlimate_climate_db.community_vulnerability_assessments
ORDER BY assessment_date DESC
    ''',
    
    'carbon_footprint': '''
-- Carbon Footprint Dataset
SELECT 
    energy_type,
    carbon_intensity_trend,
    climate_resilience,
    transition_opportunities,
    carbon_risk_score,
    key_insights,
    assessment_date
FROM africlimate_climate_db.carbon_impact_assessments
ORDER BY assessment_date DESC
    '''
}

# Dashboard Visualization Specifications
DASHBOARD_VISUALIZATIONS = {
    'main_dashboard': {
        'title': 'AfriClimate Analytics Lake - Comprehensive Platform',
        'visualizations': [
            {
                'name': 'Drought Risk Map',
                'type': 'Map',
                'dataset': 'drought_early_warning',
                'dimensions': ['province', 'region'],
                'measures': ['monthly_precip', 'avg_spi'],
                'color': 'risk_level',
                'description': 'Real-time drought risk across Southern Africa provinces'
            },
            {
                'name': 'Water Security Gauge',
                'type': 'Gauge',
                'dataset': 'water_security',
                'measure': 'current_capacity_percent',
                'dimension': 'dam_name',
                'description': 'Current dam capacity levels across South Africa'
            },
            {
                'name': 'NDVI Vegetation Health',
                'type': 'Line Chart',
                'dataset': 'ndvi_impact_tracker',
                'x_axis': 'assessment_date',
                'y_axis': 'overall_metrics',
                'series': 'ecosystem',
                'description': 'Vegetation health trends in conservation areas'
            },
            {
                'name': 'Community Risk Assessment',
                'type': 'Bar Chart',
                'dataset': 'community_adaptation',
                'x_axis': 'settlement_name',
                'y_axis': 'population',
                'color': 'overall_risk_level',
                'description': 'Climate vulnerability in informal settlements'
            },
            {
                'name': 'Carbon Footprint Analysis',
                'type': 'Scatter Plot',
                'dataset': 'carbon_footprint',
                'x_axis': 'climate_resilience',
                'y_axis': 'carbon_risk_score',
                'size': 'energy_type',
                'description': 'Energy production vs. climate impact correlation'
            },
            {
                'name': 'Alert Summary KPI',
                'type': 'KPI',
                'datasets': ['all'],
                'measure': 'count_high_risk',
                'description': 'Summary of all active climate alerts'
            },
            {
                'name': 'Regional Climate Trends',
                'type': 'Combo Chart',
                'dataset': 'drought_early_warning',
                'x_axis': 'analysis_date',
                'y_axis_measures': ['monthly_precip', 'avg_spi'],
                'description': 'Historical climate trends and patterns'
            },
            {
                'name': 'Stakeholder Impact Matrix',
                'type': 'Heatmap',
                'datasets': ['all'],
                'rows': 'stakeholder_type',
                'columns': 'risk_category',
                'values': 'impact_score',
                'description': 'Cross-sector climate impact assessment'
            }
        ]
    },
    
    'stakeholder_dashboards': {
        'farmer_dashboard': {
            'title': 'Farmer Climate Intelligence',
            'audience': 'Farmers & Agricultural Organizations',
            'access_level': 'Public',
            'visualizations': ['Drought Risk Map', 'Regional Climate Trends', 'Alert Summary KPI']
        },
        'municipal_dashboard': {
            'title': 'Municipal Water Management',
            'audience': 'City Officials & Water Authorities',
            'access_level': 'Restricted',
            'visualizations': ['Water Security Gauge', 'Regional Climate Trends', 'Alert Summary KPI']
        },
        'conservation_dashboard': {
            'title': 'Biodiversity & Conservation',
            'audience': 'Conservation Organizations & Researchers',
            'access_level': 'Restricted',
            'visualizations': ['NDVI Vegetation Health', 'Stakeholder Impact Matrix', 'Alert Summary KPI']
        },
        'community_dashboard': {
            'title': 'Community Climate Resilience',
            'audience': 'Community Leaders & NGOs',
            'access_level': 'Public',
            'visualizations': ['Community Risk Assessment', 'Alert Summary KPI', 'Regional Climate Trends']
        },
        'executive_dashboard': {
            'title': 'Executive Climate Platform',
            'audience': 'Policy Makers & Senior Officials',
            'access_level': 'Executive',
            'visualizations': ['All visualizations']
        }
    }
}

def save_quicksight_queries():
    """Save SQL queries to files for QuickSight setup"""
    
    print("📊 Generating QuickSight SQL Queries...")
    
    for dataset_name, query in QUICKSIGHT_QUERIES.items():
        filename = f"quicksight_queries_{dataset_name}.sql"
        
        with open(filename, 'w') as f:
            f.write(f"-- {dataset_name.replace('_', ' ').title()}\n")
            f.write(f"-- AfriClimate Analytics Lake\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(query)
        
        print(f"✅ Saved: {filename}")
    
    return len(QUICKSIGHT_QUERIES)

def save_dashboard_config():
    """Save dashboard configuration for QuickSight setup"""
    
    print("📈 Generating Dashboard Configuration...")
    
    with open('quicksight_dashboard_config.json', 'w') as f:
        json.dump(DASHBOARD_VISUALIZATIONS, f, indent=2)
    
    print("✅ Saved: quicksight_dashboard_config.json")
    
    return True

def create_setup_checklist():
    """Create QuickSight setup checklist"""
    
    checklist = """
# 📊 QuickSight Setup Checklist

## 🔧 Account Setup
- [ ] Sign up for QuickSight (https://console.aws.amazon.com/quicksight/)
- [ ] Select region: af-south-1
- [ ] Account name: AfriClimate Analytics Lake
- [ ] Edition: Standard (free trial)
- [ ] Add your email for notifications

## 🔗 Data Connection
- [ ] Click "New dataset"
- [ ] Select "Athena"
- [ ] Data source name: AfriClimate-Data
- [ ] Workgroup: primary
- [ ] Database: africlimate_climate_db
- [ ] Click "Create data source"

## 📊 Dataset Creation
- [ ] Create 5 datasets using SQL queries:
  - [ ] Drought Early Warning (drought_early_warning.sql)
  - [ ] Water Security (water_security.sql)
  - [ ] NDVI Impact Tracker (ndvi_impact_tracker.sql)
  - [ ] Community Adaptation (community_adaptation.sql)
  - [ ] Carbon Footprint (carbon_footprint.sql)

## 📈 Dashboard Creation
- [ ] Create main dashboard with 8 visualizations:
  - [ ] Drought Risk Map
  - [ ] Water Security Gauge
  - [ ] NDVI Vegetation Health
  - [ ] Community Risk Assessment
  - [ ] Carbon Footprint Analysis
  - [ ] Alert Summary KPI
  - [ ] Regional Climate Trends
  - [ ] Stakeholder Impact Matrix

## 👥 Stakeholder Dashboards
- [ ] Create 5 specialized dashboards:
  - [ ] Farmer Dashboard (Public)
  - [ ] Municipal Dashboard (Restricted)
  - [ ] Conservation Dashboard (Restricted)
  - [ ] Community Dashboard (Public)
  - [ ] Executive Dashboard (Executive)

## 🔐 Security Setup
- [ ] Set up row-level security
- [ ] Configure user permissions
  - [ ] Public access for farmer/community dashboards
  - [ ] Restricted access for municipal/conservation
  - [ ] Executive access for policy makers

## 📱 Testing
- [ ] Test all visualizations load correctly
- [ ] Test filters work as expected
- [ ] Test drill-downs provide insights
- [ ] Test sharing permissions work
- [ ] Test mobile responsiveness

## 🚀 Publishing
- [ ] Publish main dashboard
- [ ] Generate share links
- [ ] Test share functionality
- [ ] Document dashboard usage

## 📋 Documentation
- [ ] Create user guide
- [ ] Document data sources
- [ ] Create troubleshooting guide
- [ ] Record setup process

---

## 🎯 Expected Outcome
After completion, you'll have:
- 1 main dashboard with 8 interactive visualizations
- 5 stakeholder-specific dashboards
- Real South African climate data integration
- Multi-level security and permissions
- Professional, production-ready climate intelligence platform

## 🚀 Next Steps
After QuickSight setup:
- Test end-to-end pipeline
- Document dashboard usage
- Prepare presentation materials
- Final GitHub commit
"""
    
    with open('QUICKSIGHT_SETUP_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Saved: QUICKSIGHT_SETUP_CHECKLIST.md")

def main():
    """Main function to generate all QuickSight setup files"""
    
    print("🚀 AfriClimate Analytics Lake - QuickSight Setup Generator")
    print("=" * 60)
    
    # Generate SQL queries
    query_count = save_quicksight_queries()
    
    # Save dashboard configuration
    save_dashboard_config()
    
    # Create setup checklist
    create_setup_checklist()
    
    print(f"\n🎉 QuickSight Setup Files Generated:")
    print(f"📊 SQL Queries: {query_count} files")
    print(f"📈 Dashboard Config: 1 file")
    print(f"📋 Setup Checklist: 1 file")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. 🌐 Open QuickSight: https://console.aws.amazon.com/quicksight/")
    print(f"2. 📊 Follow QUICKSIGHT_SETUP_CHECKLIST.md")
    print(f"3. 🔗 Use generated SQL queries for datasets")
    print(f"4. 📈 Build dashboards using configuration")
    print(f"5. 🚀 Test and publish dashboards")

if __name__ == "__main__":
    main()
