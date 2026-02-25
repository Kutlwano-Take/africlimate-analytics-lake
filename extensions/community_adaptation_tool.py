#!/usr/bin/env python3
"""
Community Climate Adaptation Tool Lambda Function
Maps water access points and vulnerability in informal settlements
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
BUCKET_NAME = 'africlimate-analytics-lake'

# Major informal settlements in Southern Africa
INFORMAL_SETTLEMENTS = {
    'khayelitsha': {
        'name': 'Khayelitsha',
        'city': 'Cape Town',
        'country': 'South Africa',
        'latitude': -34.0397,
        'longitude': 18.6667,
        'population_estimate': 400000,
        'households': 100000,
        'water_access_score': 0.6  # 0-1 scale
    },
    'soweto': {
        'name': 'Soweto',
        'city': 'Johannesburg',
        'country': 'South Africa',
        'latitude': -26.2678,
        'longitude': 27.8585,
        'population_estimate': 1200000,
        'households': 300000,
        'water_access_score': 0.7
    },
    'diepsloot': {
        'name': 'Diepsloot',
        'city': 'Johannesburg',
        'country': 'South Africa',
        'latitude': -25.9333,
        'longitude': 28.0167,
        'population_estimate': 350000,
        'households': 87500,
        'water_access_score': 0.5
    },
    'tembisa': {
        'name': 'Tembisa',
        'city': 'Johannesburg',
        'country': 'South Africa',
        'latitude': -26.3583,
        'longitude': 28.2333,
        'population_estimate': 463000,
        'households': 115750,
        'water_access_score': 0.65
    },
    'khutsong': {
        'name': 'Khutsong',
        'city': 'Carletonville',
        'country': 'South Africa',
        'latitude': -26.8333,
        'longitude': 27.4500,
        'population_estimate': 140000,
        'households': 35000,
        'water_access_score': 0.55
    }
}

def fetch_water_access_points():
    """Fetch water access points for informal settlements"""
    logger.info("Mapping water access points...")
    
    water_access_data = []
    
    for settlement_id, settlement_info in INFORMAL_SETTLEMENTS.items():
        # Calculate water points based on population and access score
        population = settlement_info['population_estimate']
        access_score = settlement_info['water_access_score']
        
        # Estimated water points (taps, wells, etc.)
        total_water_points = int((population / 200) * access_score)  # 1 point per 200 people
        functional_points = int(total_water_points * 0.8)  # 80% functional
        
        water_access_record = {
            'settlement_id': settlement_id,
            'settlement_name': settlement_info['name'],
            'city': settlement_info['city'],
            'country': settlement_info['country'],
            'latitude': settlement_info['latitude'],
            'longitude': settlement_info['longitude'],
            'population': population,
            'households': settlement_info['households'],
            'total_water_points': total_water_points,
            'functional_water_points': functional_points,
            'people_per_water_point': round(population / max(1, functional_points), 1),
            'water_access_score': access_score,
            'data_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        water_access_data.append(water_access_record)
    
    return water_access_data

def fetch_climate_vulnerability():
    """Assess climate vulnerability for settlements"""
    logger.info("Assessing climate vulnerability...")
    
    vulnerability_data = []
    current_date = datetime.now()
    
    for settlement_id, settlement_info in INFORMAL_SETTLEMENTS.items():
        lat = settlement_info['latitude']
        
        # Climate vulnerability factors
        drought_risk = 0.7 if lat < -25 else 0.5  # Higher drought risk in northern areas
        flood_risk = 0.6 if lat > -30 else 0.4    # Higher flood risk in southern areas
        heat_stress = 0.5 + abs(lat) * 0.01       # Heat stress increases with latitude distance from equator
        
        # Infrastructure vulnerability
        infrastructure_score = 0.4  # Generally poor in informal settlements
        water_infrastructure_vulnerability = 1 - settlement_info['water_access_score']
        
        # Social vulnerability
        population_density = settlement_info['population_estimate'] / 5  # Approximate km²
        social_vulnerability = min(1.0, population_density / 100000)  # Higher density = higher vulnerability
        
        # Overall vulnerability score
        overall_vulnerability = (
            drought_risk * 0.3 +
            flood_risk * 0.2 +
            heat_stress * 0.2 +
            infrastructure_score * 0.15 +
            water_infrastructure_vulnerability * 0.1 +
            social_vulnerability * 0.05
        )
        
        vulnerability_record = {
            'settlement_id': settlement_id,
            'settlement_name': settlement_info['name'],
            'city': settlement_info['city'],
            'latitude': lat,
            'longitude': settlement_info['longitude'],
            'drought_risk_score': round(drought_risk, 2),
            'flood_risk_score': round(flood_risk, 2),
            'heat_stress_score': round(heat_stress, 2),
            'infrastructure_vulnerability': round(infrastructure_score, 2),
            'water_infrastructure_vulnerability': round(water_infrastructure_vulnerability, 2),
            'social_vulnerability': round(social_vulnerability, 2),
            'overall_vulnerability_score': round(overall_vulnerability, 2),
            'vulnerability_level': 'Critical' if overall_vulnerability > 0.7 else 'High' if overall_vulnerability > 0.5 else 'Medium' if overall_vulnerability > 0.3 else 'Low',
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        vulnerability_data.append(vulnerability_record)
    
    return vulnerability_data

def generate_adaptation_strategies(water_access_data, vulnerability_data):
    """Generate community-specific adaptation strategies"""
    adaptation_data = []
    
    water_dict = {w['settlement_id']: w for w in water_access_data}
    
    for vulnerability in vulnerability_data:
        water = water_dict.get(vulnerability['settlement_id'], {})
        
        strategies = []
        priority_actions = []
        
        # Water-related adaptations
        if water.get('people_per_water_point', 0) > 500:
            strategies.append("Install communal water tanks")
            priority_actions.append("Water infrastructure upgrade")
        
        if vulnerability['drought_risk_score'] > 0.6:
            strategies.append("Rainwater harvesting systems")
            strategies.append("Water conservation education")
            priority_actions.append("Drought preparedness plan")
        
        if vulnerability['flood_risk_score'] > 0.6:
            strategies.append("Improved drainage systems")
            strategies.append("Elevated water storage")
            priority_actions.append("Flood early warning system")
        
        if vulnerability['heat_stress_score'] > 0.6:
            strategies.append("Shaded water collection points")
            strategies.append("Community cooling centers")
            priority_actions.append("Heat action plan")
        
        # Infrastructure adaptations
        if vulnerability['infrastructure_vulnerability'] > 0.5:
            strategies.append("Upgrade water distribution networks")
            strategies.append("Backup water supply systems")
        
        # Community-based adaptations
        strategies.append("Community water management committees")
        strategies.append("Water quality monitoring training")
        
        adaptation_record = {
            'settlement_id': vulnerability['settlement_id'],
            'settlement_name': vulnerability['settlement_name'],
            'city': vulnerability['city'],
            'overall_vulnerability_score': vulnerability['overall_vulnerability_score'],
            'vulnerability_level': vulnerability['vulnerability_level'],
            'people_per_water_point': water.get('people_per_water_point', 0),
            'adaptation_strategies': strategies,
            'priority_actions': priority_actions,
            'estimated_implementation_cost_usd': len(strategies) * 50000,  # Rough estimate
            'implementation_timeline_months': len(priority_actions) * 3,
            'expected_benefits': f"Improved water access for {water.get('population', 0):,} residents",
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        adaptation_data.append(adaptation_record)
    
    return adaptation_data

def store_community_adaptation_data(water_access_data, vulnerability_data, adaptation_data):
    """Store community adaptation data to S3"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    analysis_result = {
        'analysis_timestamp': datetime.now().isoformat(),
        'water_access_data': water_access_data,
        'vulnerability_data': vulnerability_data,
        'adaptation_strategies': adaptation_data,
        'summary': {
            'total_settlements_analyzed': len(adaptation_data),
            'critical_vulnerability': len([a for a in vulnerability_data if a['vulnerability_level'] == 'Critical']),
            'high_vulnerability': len([a for a in vulnerability_data if a['vulnerability_level'] == 'High']),
            'medium_vulnerability': len([a for a in vulnerability_data if a['vulnerability_level'] == 'Medium']),
            'low_vulnerability': len([a for a in vulnerability_data if a['vulnerability_level'] == 'Low']),
            'total_population_served': sum(w['population'] for w in water_access_data),
            'average_people_per_water_point': round(sum(w['people_per_water_point'] for w in water_access_data) / len(water_access_data), 1),
            'total_adaptation_strategies': sum(len(a['adaptation_strategies']) for a in adaptation_data),
            'estimated_total_cost_usd': sum(a['estimated_implementation_cost_usd'] for a in adaptation_data)
        }
    }
    
    key = f'extensions/processed/community/community_adaptation_analysis_{timestamp}.json'
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(analysis_result, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Stored community adaptation analysis to S3: {key}")
    return key

def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info("Starting Community Climate Adaptation Analysis")
    
    try:
        # Fetch water access points
        water_access_data = fetch_water_access_points()
        
        # Assess climate vulnerability
        vulnerability_data = fetch_climate_vulnerability()
        
        # Generate adaptation strategies
        adaptation_data = generate_adaptation_strategies(water_access_data, vulnerability_data)
        
        # Store results
        result_key = store_community_adaptation_data(water_access_data, vulnerability_data, adaptation_data)
        
        logger.info(f"Community adaptation analysis completed for {len(adaptation_data)} settlements")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Community adaptation analysis completed',
                'settlements_analyzed': len(adaptation_data),
                'critical_vulnerabilities': len([a for a in vulnerability_data if a['vulnerability_level'] == 'Critical']),
                'total_adaptation_strategies': sum(len(a['adaptation_strategies']) for a in adaptation_data),
                'data_location': f"s3://{BUCKET_NAME}/{result_key}"
            })
        }
        
    except Exception as e:
        logger.error(f"Error in community adaptation analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

if __name__ == "__main__":
    class MockContext:
        function_name = "community-adaptation-tool-test"
        memory_limit_in_mb = 256
        remaining_time_in_millis = 300000
    
    test_event = {}
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
