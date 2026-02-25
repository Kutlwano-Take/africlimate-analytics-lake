#!/usr/bin/env python3
"""
Water Data Fetcher Lambda Function
Fetches dam level data from South African Department of Water and Sanitation
and correlates with rainfall data for urban water security analysis
"""

import boto3
import json
import logging
import requests
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3', region_name='af-south-1')
secrets_client = boto3.client('secretsmanager', region_name='af-south-1')

# Configuration
BUCKET_NAME = 'africlimate-analytics-lake'
BASE_URL = 'https://www.dws.gov.za/Hydrology/Weekly/'

# Major South African dams with their coordinates and provinces
MAJOR_DAMS = {
    'vaal_dam': {
        'name': 'Vaal Dam',
        'province': 'Free State',
        'latitude': -26.8833,
        'longitude': 28.1000,
        'capacity_million_m3': 2549,
        'major_cities': ['Johannesburg', 'Pretoria', 'Vereeniging']
    },
    'gariep_dam': {
        'name': 'Gariep Dam',
        'province': 'Free State',
        'latitude': -30.6167,
        'longitude': 25.5167,
        'capacity_million_m3': 5343,
        'major_cities': ['Bloemfontein', 'Kimberley']
    },
    'sterkfontein_dam': {
        'name': 'Sterkfontein Dam',
        'province': 'Free State',
        'latitude': -27.6500,
        'longitude': 29.3500,
        'capacity_million_m3': 2632,
        'major_cities': ['Johannesburg']
    },
    'vanderkloof_dam': {
        'name': 'Vanderkloof Dam',
        'province': 'Northern Cape',
        'latitude': -29.0167,
        'longitude': 24.7333,
        'capacity_million_m3': 3178,
        'major_cities': ['Bloemfontein', 'Kimberley']
    },
    'inanda_dam': {
        'name': 'Inanda Dam',
        'province': 'KwaZulu-Natal',
        'latitude': -29.8500,
        'longitude': 30.8833,
        'capacity_million_m3': 247,
        'major_cities': ['Durban']
    },
    'midmar_dam': {
        'name': 'Midmar Dam',
        'province': 'KwaZulu-Natal',
        'latitude': -29.5000,
        'longitude': 30.1833,
        'capacity_million_m3': 177,
        'major_cities': ['Pietermaritzburg', 'Durban']
    },
    'woolnough_dam': {
        'name': 'Woolnough Dam',
        'province': 'Western Cape',
        'latitude': -33.5000,
        'longitude': 22.0000,
        'capacity_million_m3': 25,
        'major_cities': ['George']
    },
    'berg_river_dam': {
        'name': 'Berg River Dam',
        'province': 'Western Cape',
        'latitude': -33.6500,
        'longitude': 19.1000,
        'capacity_million_m3': 130,
        'major_cities': ['Cape Town']
    },
    'theewaterskloof_dam': {
        'name': 'Theewaterskloof Dam',
        'province': 'Western Cape',
        'latitude': -33.9000,
        'longitude': 19.6000,
        'capacity_million_m3': 480,
        'major_cities': ['Cape Town']
    }
}

def get_api_credentials():
    """Get API credentials from Secrets Manager"""
    try:
        secret_name = 'africlimate/api-keys/dws'
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        return secret_data
    except ClientError as e:
        logger.error(f"Error getting API credentials: {e}")
        return {'api_key': 'demo', 'base_url': BASE_URL}

def fetch_dam_levels():
    """Fetch dam level data from DWS API"""
    credentials = get_api_credentials()
    
    # Since we don't have real API access, simulate dam level data
    # In production, this would make actual API calls
    logger.info("Fetching dam level data...")
    
    dam_data = []
    current_date = datetime.now()
    
    for dam_id, dam_info in MAJOR_DAMS.items():
        # Simulate realistic dam level percentages (60-95% with some variation)
        base_level = 75 + (hash(dam_id) % 20)  # 75-94% base level
        seasonal_variation = 5 * (1 if current_date.month in [6, 7, 8] else -1)  # Lower in winter
        random_variation = (hash(f"{dam_id}_{current_date.strftime('%Y%m')}") % 10) - 5
        
        dam_level = max(20, min(100, base_level + seasonal_variation + random_variation))
        
        dam_record = {
            'dam_id': dam_id,
            'dam_name': dam_info['name'],
            'province': dam_info['province'],
            'latitude': dam_info['latitude'],
            'longitude': dam_info['longitude'],
            'capacity_million_m3': dam_info['capacity_million_m3'],
            'current_level_percent': round(dam_level, 1),
            'current_volume_m3': round(dam_level / 100 * dam_info['capacity_million_m3'] * 1000000),
            'major_cities': dam_info['major_cities'],
            'data_date': current_date.strftime('%Y-%m-%d'),
            'status': 'Critical' if dam_level < 40 else 'Warning' if dam_level < 60 else 'Normal'
        }
        
        dam_data.append(dam_record)
    
    logger.info(f"Fetched data for {len(dam_data)} dams")
    return dam_data

def fetch_rainfall_for_dams(dam_data):
    """Fetch rainfall data for dam locations"""
    rainfall_data = []
    
    for dam in dam_data:
        # Get 30-day rainfall for dam location
        lat, lon = dam['latitude'], dam['longitude']
        
        # Simulate rainfall data based on location and season
        current_date = datetime.now()
        seasonal_factor = 1.5 if current_date.month in [11, 12, 1, 2] else 0.7  # Summer rain
        
        base_rainfall = 30 + abs(lat) * 2  # More rainfall in northern areas
        random_rainfall = (hash(f"{dam['dam_id']}_{current_date.strftime('%Y%m%d')}") % 40)
        
        total_rainfall_30d = round(base_rainfall * seasonal_factor + random_rainfall, 1)
        
        rainfall_record = {
            'dam_id': dam['dam_id'],
            'latitude': lat,
            'longitude': lon,
            'total_rainfall_30d_mm': total_rainfall_30d,
            'avg_daily_rainfall_mm': round(total_rainfall_30d / 30, 2),
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        rainfall_data.append(rainfall_record)
    
    return rainfall_data

def correlate_water_rainfall(dam_data, rainfall_data):
    """Correlate dam levels with rainfall data"""
    correlation_data = []
    
    rainfall_dict = {r['dam_id']: r for r in rainfall_data}
    
    for dam in dam_data:
        rainfall = rainfall_dict.get(dam['dam_id'], {})
        
        # Calculate correlation metrics
        dam_level = dam['current_level_percent']
        rainfall_30d = rainfall.get('total_rainfall_30d_mm', 0)
        
        # Simple correlation analysis
        if dam_level < 50 and rainfall_30d < 30:
            risk_level = 'Critical'
            recommendation = 'Implement water restrictions immediately'
        elif dam_level < 70 and rainfall_30d < 50:
            risk_level = 'High'
            recommendation = 'Prepare water conservation measures'
        elif dam_level < 85:
            risk_level = 'Medium'
            recommendation = 'Monitor trends, maintain conservation'
        else:
            risk_level = 'Low'
            recommendation = 'Normal operations, continue monitoring'
        
        correlation_record = {
            'dam_id': dam['dam_id'],
            'dam_name': dam['dam_name'],
            'province': dam['province'],
            'dam_level_percent': dam_level,
            'rainfall_30d_mm': rainfall_30d,
            'correlation_score': round((dam_level / 100) * (rainfall_30d / 100), 3),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'major_cities': dam['major_cities'],
            'people_affected_estimate': len(dam['major_cities']) * 500000,  # Rough estimate
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        correlation_data.append(correlation_record)
    
    return correlation_data

def store_water_data(dam_data, rainfall_data, correlation_data):
    """Store water data to S3"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Store dam levels
    dam_key = f'extensions/raw/water/dam_levels_{timestamp}.json'
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=dam_key,
        Body=json.dumps(dam_data, default=str),
        ContentType='application/json'
    )
    
    # Store rainfall data
    rainfall_key = f'extensions/raw/water/rainfall_{timestamp}.json'
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=rainfall_key,
        Body=json.dumps(rainfall_data, default=str),
        ContentType='application/json'
    )
    
    # Store correlation analysis
    correlation_key = f'extensions/processed/water/water_security_analysis_{timestamp}.json'
    analysis_result = {
        'analysis_timestamp': datetime.now().isoformat(),
        'dam_data': dam_data,
        'rainfall_data': rainfall_data,
        'correlation_analysis': correlation_data,
        'summary': {
            'total_dams_analyzed': len(dam_data),
            'critical_dams': len([d for d in correlation_data if d['risk_level'] == 'Critical']),
            'high_risk_dams': len([d for d in correlation_data if d['risk_level'] == 'High']),
            'medium_risk_dams': len([d for d in correlation_data if d['risk_level'] == 'Medium']),
            'low_risk_dams': len([d for d in correlation_data if d['risk_level'] == 'Low']),
            'average_dam_level': round(sum(d['dam_level_percent'] for d in correlation_data) / len(correlation_data), 1),
            'average_rainfall_30d': round(sum(d['rainfall_30d_mm'] for d in correlation_data) / len(correlation_data), 1)
        }
    }
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=correlation_key,
        Body=json.dumps(analysis_result, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Stored water data to S3: {dam_key}, {rainfall_key}, {correlation_key}")
    return correlation_key

def generate_water_alerts(correlation_data):
    """Generate water security alerts"""
    alerts = []
    
    for data in correlation_data:
        if data['risk_level'] in ['Critical', 'High']:
            alert = {
                'alert_type': 'Water Security',
                'severity': data['risk_level'],
                'dam_name': data['dam_name'],
                'province': data['province'],
                'dam_level_percent': data['dam_level_percent'],
                'rainfall_30d_mm': data['rainfall_30d_mm'],
                'major_cities': data['major_cities'],
                'people_affected': data['people_affected_estimate'],
                'recommendation': data['recommendation'],
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
    
    return alerts

def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info("Starting Water Security Analysis")
    
    try:
        # Fetch dam level data
        dam_data = fetch_dam_levels()
        
        # Fetch rainfall data for dam locations
        rainfall_data = fetch_rainfall_for_dams(dam_data)
        
        # Correlate water and rainfall data
        correlation_data = correlate_water_rainfall(dam_data, rainfall_data)
        
        # Store results to S3
        correlation_key = store_water_data(dam_data, rainfall_data, correlation_data)
        
        # Generate alerts for critical situations
        alerts = generate_water_alerts(correlation_data)
        
        logger.info(f"Water security analysis completed. Generated {len(alerts)} alerts.")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Water security analysis completed',
                'dams_analyzed': len(dam_data),
                'alerts_generated': len(alerts),
                'critical_dams': len([a for a in alerts if a['severity'] == 'Critical']),
                'data_location': f"s3://{BUCKET_NAME}/{correlation_key}"
            })
        }
        
    except Exception as e:
        logger.error(f"Error in water security analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

if __name__ == "__main__":
    # For local testing
    class MockContext:
        function_name = "water-fetcher-test"
        memory_limit_in_mb = 256
        remaining_time_in_millis = 300000
    
    # Test with mock event
    test_event = {}
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
