#!/usr/bin/env python3
"""
Carbon Footprint Integration Lambda Function
Tracks energy usage/emissions with climate data for policy makers
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

# Southern African countries with energy data
COUNTRIES = {
    'south_africa': {
        'name': 'South Africa',
        'population_millions': 60.0,
        'gdp_billion_usd': 419,
        'main_energy_sources': ['coal', 'renewable', 'nuclear', 'gas'],
        'coal_percentage': 85  # High coal dependency
    },
    'botswana': {
        'name': 'Botswana',
        'population_millions': 2.4,
        'gdp_billion_usd': 17,
        'main_energy_sources': ['coal', 'imported_electricity'],
        'coal_percentage': 70
    },
    'namibia': {
        'name': 'Namibia',
        'population_millions': 2.5,
        'gdp_billion_usd': 12,
        'main_energy_sources': ['imported_electricity', 'renewable', 'hydro'],
        'coal_percentage': 20
    },
    'zimbabwe': {
        'name': 'Zimbabwe',
        'population_millions': 15.0,
        'gdp_billion_usd': 26,
        'main_energy_sources': ['coal', 'hydro', 'imported_electricity'],
        'coal_percentage': 60
    },
    'zambia': {
        'name': 'Zambia',
        'population_millions': 18.0,
        'gdp_billion_usd': 23,
        'main_energy_sources': ['hydro', 'coal', 'imported_electricity'],
        'coal_percentage': 30
    }
}

def fetch_energy_consumption():
    """Fetch energy consumption and emissions data"""
    logger.info("Fetching energy consumption and emissions data...")
    
    energy_data = []
    current_date = datetime.now()
    
    for country_id, country_info in COUNTRIES.items():
        # Simulate energy consumption data
        population = country_info['population_millions']
        gdp = country_info['gdp_billion_usd']
        
        # Energy consumption (TWh per year) - realistic estimates
        base_consumption = population * 4.5  # MWh per person per year
        economic_factor = gdp / 100  # Economic activity factor
        total_consumption_twh = base_consumption + economic_factor
        
        # Emissions by source
        coal_emissions = (total_consumption_twh * country_info['coal_percentage'] / 100) * 0.9  # 0.9 tCO2/MWh for coal
        other_emissions = (total_consumption_twh * (1 - country_info['coal_percentage'] / 100)) * 0.4  # 0.4 tCO2/MWh average
        total_emissions_mt = coal_emissions + other_emissions
        
        # Seasonal variation (higher emissions in winter due to heating)
        seasonal_factor = 1.2 if current_date.month in [6, 7, 8] else 0.9
        adjusted_emissions = total_emissions_mt * seasonal_factor
        
        energy_record = {
            'country_id': country_id,
            'country_name': country_info['name'],
            'population_millions': population,
            'gdp_billion_usd': gdp,
            'total_energy_consumption_twh': round(total_consumption_twh, 2),
            'coal_consumption_twh': round(total_consumption_twh * country_info['coal_percentage'] / 100, 2),
            'renewable_consumption_twh': round(total_consumption_twh * 0.1, 2),  # Assume 10% renewable
            'total_emissions_mt_co2': round(adjusted_emissions, 2),
            'coal_emissions_mt_co2': round(coal_emissions * seasonal_factor, 2),
            'renewable_emissions_mt_co2': round(total_consumption_twh * 0.1 * 0.05, 2),  # 0.05 tCO2/MWh for renewable
            'emissions_per_capita_tonnes': round(adjusted_emissions * 1000000 / (population * 1000000), 2),
            'emissions_intensity_tco2_per_gdp': round(adjusted_emissions / gdp, 3),
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        energy_data.append(energy_record)
    
    return energy_data

def fetch_climate_correlation():
    """Correlate emissions with climate data"""
    logger.info("Analyzing climate-emissions correlations...")
    
    climate_correlation = []
    current_date = datetime.now()
    
    for country_id, country_info in COUNTRIES.items():
        # Simulate climate data for each country
        # Temperature anomaly (°C above pre-industrial)
        temp_anomaly = 1.2 + (hash(country_id) % 100) / 200  # 1.2-1.7°C range
        
        # Extreme weather events (count per year)
        extreme_events = 5 + int(temp_anomaly * 3)  # More events with higher warming
        
        # Renewable energy potential affected by climate
        solar_potential_change = 1.0 + (temp_anomaly * 0.05)  # Slight increase with warming
        hydro_potential_change = 1.0 - (temp_anomaly * 0.1)   # Decrease with drought risk
        
        # Climate impact on energy demand
        cooling_demand_increase = temp_anomaly * 0.08  # 8% increase per degree
        heating_demand_decrease = temp_anomaly * 0.03  # 3% decrease per degree
        
        correlation_record = {
            'country_id': country_id,
            'country_name': country_info['name'],
            'temperature_anomaly_c': round(temp_anomaly, 2),
            'extreme_weather_events_year': extreme_events,
            'solar_potential_change_factor': round(solar_potential_change, 3),
            'hydro_potential_change_factor': round(hydro_potential_change, 3),
            'cooling_demand_increase_percent': round(cooling_demand_increase * 100, 1),
            'heating_demand_decrease_percent': round(heating_demand_decrease * 100, 1),
            'climate_risk_level': 'High' if temp_anomaly > 1.5 else 'Medium' if temp_anomaly > 1.2 else 'Low',
            'data_date': current_date.strftime('%Y-%m-%d')
        }
        
        climate_correlation.append(correlation_record)
    
    return climate_correlation

def analyze_carbon_footprint(energy_data, climate_correlation):
    """Analyze carbon footprint with climate correlations"""
    footprint_analysis = []
    current_date = datetime.now()
    
    energy_dict = {e['country_id']: e for e in energy_data}
    climate_dict = {c['country_id']: c for c in climate_correlation}
    
    for country_id in COUNTRIES.keys():
        energy = energy_dict.get(country_id, {})
        climate = climate_dict.get(country_id, {})
        
        # Calculate adjusted emissions based on climate factors
        base_emissions = energy.get('total_emissions_mt_co2', 0)
        cooling_factor = 1 + (climate.get('cooling_demand_increase_percent', 0) / 100)
        climate_adjusted_emissions = base_emissions * cooling_factor
        
        # Renewable energy opportunity
        current_renewable = energy.get('renewable_consumption_twh', 0)
        solar_potential = current_renewable * climate.get('solar_potential_change_factor', 1.0)
        renewable_opportunity_twh = solar_potential - current_renewable
        
        # Emission reduction potential
        coal_emissions = energy.get('coal_emissions_mt_co2', 0)
        renewable_potential_emissions_reduction = renewable_opportunity_twh * 0.85  # 0.85 tCO2/MWh avoided from coal
        
        # Policy recommendations
        recommendations = []
        if coal_emissions > base_emissions * 0.5:
            recommendations.append("Accelerate coal-to-renewable transition")
        if renewable_opportunity_twh > 5:
            recommendations.append("Expand solar and wind capacity")
        if climate.get('climate_risk_level') == 'High':
            recommendations.append("Implement climate adaptation measures")
        recommendations.append("Enhance energy efficiency programs")
        
        # Carbon budget analysis
        paris_agreement_budget = energy.get('population_millions', 0) * 2  # 2 tonnes per person target
        current_per_capita = energy.get('emissions_per_capita_tonnes', 0)
        budget_status = "Exceeded" if current_per_capita > paris_agreement_budget else "On Track" if current_per_capita > paris_agreement_budget * 0.8 else "Well Below"
        
        analysis_record = {
            'country_id': country_id,
            'country_name': energy.get('country_name', climate.get('country_name', 'Unknown')),
            'base_emissions_mt_co2': energy.get('total_emissions_mt_co2', 0),
            'climate_adjusted_emissions_mt_co2': round(climate_adjusted_emissions, 2),
            'emissions_per_capita_tonnes': energy.get('emissions_per_capita_tonnes', 0),
            'paris_agreement_budget_per_capita': paris_agreement_budget,
            'carbon_budget_status': budget_status,
            'renewable_energy_opportunity_twh': round(renewable_opportunity_twh, 2),
            'potential_emissions_reduction_mt_co2': round(renewable_potential_emissions_reduction, 2),
            'climate_risk_level': climate.get('climate_risk_level', 'Unknown'),
            'temperature_anomaly_c': climate.get('temperature_anomaly_c', 0),
            'policy_recommendations': recommendations,
            'net_zero_timeline_years': 2050 - current_date.year,
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        footprint_analysis.append(analysis_record)
    
    return footprint_analysis

def store_carbon_footprint_data(energy_data, climate_correlation, footprint_analysis):
    """Store carbon footprint data to S3"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    analysis_result = {
        'analysis_timestamp': datetime.now().isoformat(),
        'energy_data': energy_data,
        'climate_correlation': climate_correlation,
        'footprint_analysis': footprint_analysis,
        'summary': {
            'total_countries_analyzed': len(footprint_analysis),
            'total_regional_emissions_mt_co2': sum(a['climate_adjusted_emissions_mt_co2'] for a in footprint_analysis),
            'average_emissions_per_capita': round(sum(a['emissions_per_capita_tonnes'] for a in footprint_analysis) / len(footprint_analysis), 2),
            'countries_exceeding_paris_budget': len([a for a in footprint_analysis if a['carbon_budget_status'] == 'Exceeded']),
            'total_renewable_opportunity_twh': round(sum(a['renewable_energy_opportunity_twh'] for a in footprint_analysis), 2),
            'total_potential_emissions_reduction_mt_co2': round(sum(a['potential_emissions_reduction_mt_co2'] for a in footprint_analysis), 2),
            'high_climate_risk_countries': len([a for a in footprint_analysis if a['climate_risk_level'] == 'High']),
            'total_policy_recommendations': sum(len(a['policy_recommendations']) for a in footprint_analysis)
        }
    }
    
    key = f'extensions/processed/energy/carbon_footprint_analysis_{timestamp}.json'
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(analysis_result, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Stored carbon footprint analysis to S3: {key}")
    return key

def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info("Starting Carbon Footprint Analysis")
    
    try:
        # Fetch energy consumption data
        energy_data = fetch_energy_consumption()
        
        # Fetch climate correlation data
        climate_correlation = fetch_climate_correlation()
        
        # Analyze carbon footprint
        footprint_analysis = analyze_carbon_footprint(energy_data, climate_correlation)
        
        # Store results
        result_key = store_carbon_footprint_data(energy_data, climate_correlation, footprint_analysis)
        
        logger.info(f"Carbon footprint analysis completed for {len(footprint_analysis)} countries")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Carbon footprint analysis completed',
                'countries_analyzed': len(footprint_analysis),
                'total_regional_emissions_mt_co2': sum(a['climate_adjusted_emissions_mt_co2'] for a in footprint_analysis),
                'countries_exceeding_paris_budget': len([a for a in footprint_analysis if a['carbon_budget_status'] == 'Exceeded']),
                'data_location': f"s3://{BUCKET_NAME}/{result_key}"
            })
        }
        
    except Exception as e:
        logger.error(f"Error in carbon footprint analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

if __name__ == "__main__":
    class MockContext:
        function_name = "carbon-footprint-integration-test"
        memory_limit_in_mb = 256
        remaining_time_in_millis = 300000
    
    test_event = {}
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
