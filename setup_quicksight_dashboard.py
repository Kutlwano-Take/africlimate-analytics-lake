#!/usr/bin/env python3
"""
AfriClimate Analytics Lake - QuickSight Dashboard Setup
Creates comprehensive dashboard with all 5 creative extensions
"""

import boto3
import json
from datetime import datetime

# Configuration
AWS_REGION = 'af-south-1'
QUICKSIGHT_NAMESPACE = 'default'
DATASET_NAME = 'africlimate_comprehensive_analytics'

def create_quicksight_datasets():
    """Create QuickSight datasets for all extensions"""
    
    quicksight_client = boto3.client('quicksight', region_name=AWS_REGION)
    athena_client = boto3.client('athena', region_name=AWS_REGION)
    
    print("📊 Creating QuickSight Datasets...")
    print("=" * 40)
    
    # Get account ID
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # Define datasets for each extension
    datasets = [
        {
            'name': 'drought_early_warning',
            'sql_query': '''
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
            'description': 'Drought Early Warning System - Farmer alerts and risk assessments'
        },
        {
            'name': 'water_security',
            'sql_query': '''
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
            'description': 'Urban Water Security - Dam levels and rainfall correlations'
        },
        {
            'name': 'ndvi_impact_tracker',
            'sql_query': '''
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
            'description': 'Climate Change Impact Tracker - NDVI vegetation analysis'
        },
        {
            'name': 'community_adaptation',
            'sql_query': '''
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
            'description': 'Community Climate Adaptation - Informal settlement risk assessments'
        },
        {
            'name': 'carbon_footprint',
            'sql_query': '''
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
            ''',
            'description': 'Carbon Footprint Integration - Energy-climate correlations'
        }
    ]
    
    created_datasets = 0
    
    for dataset in datasets:
        try:
            # Create Athena query result location
            output_location = f's3://africlimate-analytics-lake/quicksight-results/{dataset["name"]}/'
            
            # Execute query to create temporary table
            query_execution_id = athena_client.start_query_execution(
                QueryString=dataset['sql_query'],
                QueryExecutionContext={'Database': 'africlimate_climate_db'},
                ResultConfiguration={'OutputLocation': output_location}
            )['QueryExecutionId']
            
            print(f"🔍 Query started for {dataset['name']}: {query_execution_id}")
            
            # Create QuickSight dataset
            dataset_config = {
                'AwsAccountId': account_id,
                'DataSetId': f"africlimate_{dataset['name']}",
                'Name': f"AfriClimate - {dataset['name'].replace('_', ' ').title()}",
                'PhysicalTableMap': {
                    f"{dataset['name']}_table": {
                        'RelationalTable': {
                            'DataSourceArn': f'arn:aws:quicksight:{AWS_REGION}:{account_id}:datasource/{account_id}-{QUICKSIGHT_NAMESPACE}-Athena',
                            'Name': dataset['name'],
                            'InputColumns': [
                                {'Name': 'analysis_date', 'Type': 'STRING'},
                                {'Name': 'risk_level', 'Type': 'STRING'},
                                {'Name': 'province', 'Type': 'STRING'},
                                {'Name': 'region', 'Type': 'STRING'},
                                {'Name': 'drought_level', 'Type': 'STRING'},
                                {'Name': 'monthly_precip', 'Type': 'DECIMAL'},
                                {'Name': 'avg_spi', 'Type': 'DECIMAL'},
                                {'Name': 'farmer_message', 'Type': 'STRING'}
                            ]
                        }
                    }
                },
                'ImportMode': 'SPICE',
                'RefreshProperties': {
                    'RefreshConfiguration': {
                        'IncrementalRefresh': {
                            'LookbackWindow': 7
                        }
                    }
                }
            }
            
            # Note: In actual implementation, you'd wait for query completion first
            print(f"📊 Dataset configuration prepared for {dataset['name']}")
            created_datasets += 1
            
        except Exception as e:
            print(f"❌ Failed to create dataset {dataset['name']}: {e}")
    
    print(f"\n✅ Dataset configurations prepared: {created_datasets}/{len(datasets)}")
    return created_datasets

def create_dashboard_analysis():
    """Define dashboard analysis and visualizations"""
    
    dashboard_config = {
        'dashboard_id': 'africlimate_comprehensive_platform',
        'title': 'AfriClimate Analytics Lake - Comprehensive Climate Platform',
        'description': 'Real-time climate intelligence platform for Southern Africa',
        'visualizations': [
            {
                'title': 'Drought Early Warning Map',
                'type': 'map',
                'dataset': 'drought_early_warning',
                'metrics': ['risk_level', 'avg_spi'],
                'dimensions': ['province', 'region'],
                'description': 'Real-time drought risk across Southern Africa'
            },
            {
                'title': 'Water Security Dashboard',
                'type': 'gauge',
                'dataset': 'water_security',
                'metrics': ['current_capacity_percent', 'overall_security_score'],
                'dimensions': ['dam_name', 'province'],
                'description': 'Dam levels and water security indicators'
            },
            {
                'title': 'NDVI Vegetation Health',
                'type': 'line_chart',
                'dataset': 'ndvi_impact_tracker',
                'metrics': ['overall_metrics'],
                'dimensions': ['area_name', 'ecosystem'],
                'description': 'Vegetation health trends in conservation areas'
            },
            {
                'title': 'Community Risk Assessment',
                'type': 'bar_chart',
                'dataset': 'community_adaptation',
                'metrics': ['population'],
                'dimensions': ['settlement_name', 'overall_risk_level'],
                'description': 'Climate vulnerability in informal settlements'
            },
            {
                'title': 'Carbon Footprint Analysis',
                'type': 'scatter_plot',
                'dataset': 'carbon_footprint',
                'metrics': ['carbon_risk_score', 'climate_resilience'],
                'dimensions': ['energy_type'],
                'description': 'Energy production and carbon emission correlations'
            },
            {
                'title': 'Alert Summary Panel',
                'type': 'kpi',
                'datasets': ['drought_early_warning', 'water_security', 'community_adaptation'],
                'metrics': ['count_high_risk', 'count_alerts_sent'],
                'description': 'Summary of all active climate alerts'
            },
            {
                'title': 'Regional Climate Trends',
                'type': 'combo_chart',
                'dataset': 'drought_early_warning',
                'metrics': ['monthly_precip', 'avg_spi'],
                'dimensions': ['year', 'month'],
                'description': 'Historical climate trends and patterns'
            },
            {
                'title': 'Stakeholder Impact Matrix',
                'type': 'heatmap',
                'datasets': ['all_extensions'],
                'dimensions': ['stakeholder_type', 'risk_category'],
                'metrics': ['impact_score'],
                'description': 'Cross-sector climate impact assessment'
            }
        ]
    }
    
    # Save dashboard configuration
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    dashboard_key = f"quicksight-dashboards/{dashboard_config['dashboard_id']}-{datetime.now().strftime('%Y-%m-%d')}.json"
    
    s3_client.put_object(
        Bucket='africlimate-analytics-lake',
        Key=dashboard_key,
        Body=json.dumps(dashboard_config, indent=2),
        ContentType='application/json'
    )
    
    print(f"💾 Dashboard configuration saved: {dashboard_key}")
    return dashboard_config

def create_stakeholder_dashboards():
    """Create specialized dashboards for different stakeholder groups"""
    
    stakeholder_dashboards = [
        {
            'name': 'farmer_dashboard',
            'title': 'Farmer Climate Intelligence',
            'audience': 'Farmers & Agricultural Organizations',
            'visualizations': ['drought_map', 'rainfall_forecast', 'crop_advisory', 'alert_history'],
            'access_level': 'public'
        },
        {
            'name': 'municipal_dashboard',
            'title': 'Municipal Water Management',
            'audience': 'City Officials & Water Authorities',
            'visualizations': ['water_security', 'dam_levels', 'consumption_forecast', 'infrastructure_risk'],
            'access_level': 'restricted'
        },
        {
            'name': 'conservation_dashboard',
            'title': 'Biodiversity & Conservation',
            'audience': 'Conservation Organizations & Researchers',
            'visualizations': ['ndvi_trends', 'ecosystem_health', 'species_risk', 'habitat_changes'],
            'access_level': 'restricted'
        },
        {
            'name': 'community_dashboard',
            'title': 'Community Climate Resilience',
            'audience': 'Community Leaders & NGOs',
            'visualizations': ['settlement_risks', 'emergency_contacts', 'adaptation_resources', 'alert_system'],
            'access_level': 'public'
        },
        {
            'name': 'executive_dashboard',
            'title': 'Executive Climate Platform',
            'audience': 'Policy Makers & Senior Officials',
            'visualizations': ['all_extensions', 'cross_sector_impacts', 'policy_recommendations', 'sustainability_metrics'],
            'access_level': 'executive'
        }
    ]
    
    print("🎯 Creating Stakeholder Dashboards...")
    
    for dashboard in stakeholder_dashboards:
        print(f"  📊 {dashboard['title']} - {dashboard['audience']}")
    
    return stakeholder_dashboards

def main():
    """Main QuickSight setup function"""
    
    print("📊 AfriClimate Analytics Lake - QuickSight Dashboard Setup")
    print("=" * 60)
    
    # Create datasets
    dataset_count = create_quicksight_datasets()
    
    # Create main dashboard configuration
    main_dashboard = create_dashboard_analysis()
    
    # Create stakeholder dashboards
    stakeholder_dashboards = create_stakeholder_dashboards()
    
    print(f"\n🎉 QuickSight Setup Summary:")
    print(f"📊 Datasets configured: {dataset_count}")
    print(f"📈 Main dashboard: 8 visualizations")
    print(f"👥 Stakeholder dashboards: {len(stakeholder_dashboards)}")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. 🌐 Access QuickSight console")
    print(f"2. 📊 Create datasets using saved configurations")
    print(f"3. 📈 Build dashboards using visualization specs")
    print(f"4. 🔐 Set up row-level security for different stakeholders")
    print(f"5. 📱 Test dashboard functionality")

if __name__ == "__main__":
    main()
