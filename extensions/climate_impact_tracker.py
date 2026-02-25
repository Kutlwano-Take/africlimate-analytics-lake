#!/usr/bin/env python3
"""
Climate Change Impact Tracker Lambda Function
Blends NDVI vegetation health with long-term climate trends for conservation
"""

import boto3
import json
import logging
import requests
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3', region_name='af-south-1')
secrets_client = boto3.client('secretsmanager', region_name='af-south-1')

BUCKET_NAME = 'africlimate-analytics-lake'

# Major conservation areas in Southern Africa
CONSERVATION_AREAS = {
    'kruger_np': {
        'name': 'Kruger National Park',
        'country': 'South Africa',
        'latitude': -24.9833,
        'longitude': 31.6000,
        'area_km2': 19485,
        'ecosystem': 'Savanna'
    },
    'serengeti': {
        'name': 'Serengeti National Park',
        'country': 'Tanzania',
        'latitude': -2.3333,
        'longitude': 34.8333,
        'area_km2': 14750,
        'ecosystem': 'Savanna'
    },
    'etosha': {
        'name': 'Etosha National Park',
        'country': 'Namibia',
        'latitude': -18.8333,
        'longitude': 15.9167,
        'area_km2': 22270,
        'ecosystem': 'Savanna'
    },
    'okavango': {
        'name': 'Okavango Delta',
        'country': 'Botswana',
        'latitude': -19.3167,
        'longitude': 22.7333,
        'area_km2': 15000,
        'ecosystem': 'Wetland'
    },
    'victoria_falls': {
        'name': 'Victoria Falls National Park',
        'country': 'Zambia/Zimbabwe',
        'latitude': -17.9243,
        'longitude': 25.8567,
        'area_km2': 2300,
        'ecosystem': 'Riverine'
    }
}

def fetch_ndvi_data():
    """Fetch NDVI vegetation health data"""
    logger.info("Fetching NDVI data for conservation areas...")
    
    ndvi_data = []
    current_date = datetime.now()
    
    for area_id, area_info in CONSERVATION_AREAS.items():
        # Simulate NDVI data (0.1 = barren, 0.8 = dense vegetation)
        base_ndvi = 0.6 if area_info['ecosystem'] == 'Savanna' else 0.7
        seasonal_factor = 0.2 if current_date.month in [11, 12, 1, 2] else -0.1  # Summer greening
        climate_stress = -0.1 if area_info['ecosystem'] == 'Savanna' else -0.05
        
        ndvi_value = max(0.1, min(1.0, base_ndvi + seasonal_factor + climate_stress))
        
        ndvi_record = {
            'area_id': area_id,
            'area_name': area_info['name'],
            'country': area_info['country'],
            'latitude': area_info['latitude'],
            'longitude': area_info['longitude'],
            'ecosystem': area_info['ecosystem'],
            'ndvi_value': round(ndvi_value, 3),
            'vegetation_health': 'Excellent' if ndvi_value > 0.7 else 'Good' if ndvi_value > 0.5 else 'Poor' if ndvi_value > 0.3 else 'Critical',
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        ndvi_data.append(ndvi_record)
    
    return ndvi_data

def fetch_climate_trends():
    """Fetch long-term climate trends"""
    logger.info("Analyzing long-term climate trends...")
    
    climate_trends = []
    current_date = datetime.now()
    
    for area_id, area_info in CONSERVATION_AREAS.items():
        # Simulate 10-year climate trend analysis
        lat = area_info['latitude']
        
        # Temperature trend (°C per decade)
        temp_trend = 0.15 + abs(lat) * 0.01  # Warming trend
        
        # Precipitation trend (mm per decade)
        precip_trend = -5 - abs(lat) * 0.5  # Drying trend
        
        # Drought frequency increase
        drought_increase = 0.2 + abs(lat) * 0.02
        
        trend_record = {
            'area_id': area_id,
            'area_name': area_info['name'],
            'country': area_info['country'],
            'temperature_trend_c_per_decade': round(temp_trend, 2),
            'precipitation_trend_mm_per_decade': round(precip_trend, 1),
            'drought_frequency_increase': round(drought_increase, 3),
            'climate_risk_level': 'High' if temp_trend > 0.2 or precip_trend < -10 else 'Medium' if temp_trend > 0.1 or precip_trend < -5 else 'Low',
            'analysis_period': '2014-2024',
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        climate_trends.append(trend_record)
    
    return climate_trends

def correlate_ndvi_climate(ndvi_data, climate_trends):
    """Correlate NDVI with climate trends"""
    correlation_data = []
    
    ndvi_dict = {n['area_id']: n for n in ndvi_data}
    
    for trend in climate_trends:
        ndvi = ndvi_dict.get(trend['area_id'], {})
        
        # Calculate climate impact score
        temp_impact = trend['temperature_trend_c_per_decade'] * 2  # Temperature stress
        precip_impact = abs(trend['precipitation_trend_mm_per_decade']) * 0.05  # Drought stress
        drought_impact = trend['drought_frequency_increase'] * 10  # Drought frequency stress
        
        climate_impact_score = temp_impact + precip_impact + drought_impact
        
        # Vegetation vulnerability assessment
        ndvi_value = ndvi.get('ndvi_value', 0.5)
        vulnerability_score = climate_impact_score - (ndvi_value * 5)
        
        if vulnerability_score > 3:
            vulnerability = 'Critical'
            recommendation = 'Immediate conservation intervention required'
        elif vulnerability_score > 1.5:
            vulnerability = 'High'
            recommendation = 'Implement adaptive management strategies'
        elif vulnerability_score > 0:
            vulnerability = 'Medium'
            recommendation = 'Monitor closely, prepare contingency plans'
        else:
            vulnerability = 'Low'
            recommendation = 'Continue monitoring, maintain current practices'
        
        correlation_record = {
            'area_id': trend['area_id'],
            'area_name': trend['area_name'],
            'country': trend['country'],
            'ecosystem': ndvi.get('ecosystem', 'Unknown'),
            'current_ndvi': ndvi.get('ndvi_value', 0),
            'vegetation_health': ndvi.get('vegetation_health', 'Unknown'),
            'temperature_trend_c_per_decade': trend['temperature_trend_c_per_decade'],
            'precipitation_trend_mm_per_decade': trend['precipitation_trend_mm_per_decade'],
            'drought_frequency_increase': trend['drought_frequency_increase'],
            'climate_impact_score': round(climate_impact_score, 2),
            'vulnerability_score': round(vulnerability_score, 2),
            'vulnerability_level': vulnerability,
            'recommendation': recommendation,
            'biodiversity_risk': 'High' if vulnerability in ['Critical', 'High'] else 'Medium' if vulnerability == 'Medium' else 'Low',
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        correlation_data.append(correlation_record)
    
    return correlation_data

def store_climate_impact_data(ndvi_data, climate_trends, correlation_data):
    """Store climate impact data to S3"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    analysis_result = {
        'analysis_timestamp': datetime.now().isoformat(),
        'ndvi_data': ndvi_data,
        'climate_trends': climate_trends,
        'correlation_analysis': correlation_data,
        'summary': {
            'total_areas_analyzed': len(correlation_data),
            'critical_vulnerability': len([a for a in correlation_data if a['vulnerability_level'] == 'Critical']),
            'high_vulnerability': len([a for a in correlation_data if a['vulnerability_level'] == 'High']),
            'medium_vulnerability': len([a for a in correlation_data if a['vulnerability_level'] == 'Medium']),
            'low_vulnerability': len([a for a in correlation_data if a['vulnerability_level'] == 'Low']),
            'average_ndvi': round(sum(n['ndvi_value'] for n in ndvi_data) / len(ndvi_data), 3),
            'average_temperature_trend': round(sum(t['temperature_trend_c_per_decade'] for t in climate_trends) / len(climate_trends), 2),
            'average_precipitation_trend': round(sum(t['precipitation_trend_mm_per_decade'] for t in climate_trends) / len(climate_trends), 1)
        }
    }
    
    key = f'extensions/processed/climate/climate_impact_analysis_{timestamp}.json'
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(analysis_result, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Stored climate impact analysis to S3: {key}")
    return key

def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info("Starting Climate Change Impact Analysis")
    
    try:
        # Fetch NDVI data
        ndvi_data = fetch_ndvi_data()
        
        # Fetch climate trends
        climate_trends = fetch_climate_trends()
        
        # Correlate NDVI with climate trends
        correlation_data = correlate_ndvi_climate(ndvi_data, climate_trends)
        
        # Store results
        result_key = store_climate_impact_data(ndvi_data, climate_trends, correlation_data)
        
        logger.info(f"Climate impact analysis completed for {len(correlation_data)} conservation areas")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Climate impact analysis completed',
                'areas_analyzed': len(correlation_data),
                'critical_vulnerabilities': len([a for a in correlation_data if a['vulnerability_level'] == 'Critical']),
                'data_location': f"s3://{BUCKET_NAME}/{result_key}"
            })
        }
        
    except Exception as e:
        logger.error(f"Error in climate impact analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

if __name__ == "__main__":
    class MockContext:
        function_name = "climate-impact-tracker-test"
        memory_limit_in_mb = 256
        remaining_time_in_millis = 300000
    
    test_event = {}
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
