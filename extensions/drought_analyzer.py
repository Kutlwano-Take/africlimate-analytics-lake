#!/usr/bin/env python3
"""
Drought Early Warning System Lambda Function
Analyzes 30-day precipitation deficits and sends SMS alerts via SNS
"""

import boto3
import json
import logging
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
athena_client = boto3.client('athena', region_name='af-south-1')
sns_client = boto3.client('sns', region_name='af-south-1')
ssm_client = boto3.client('ssm', region_name='af-south-1')

# Configuration
DATABASE_NAME = 'africlimate_climate_db'
OUTPUT_LOCATION = 's3://africlimate-analytics-lake/athena-results/'
DROUGHT_THRESHOLD_MM = 50  # 50mm in 30 days = drought condition
SEVERE_DROUGHT_THRESHOLD_MM = 25  # 25mm in 30 days = severe drought

# South African provinces with their agricultural importance
PROVINCES = {
    'free_state': {'name': 'Free State', 'priority': 'HIGH', 'farmers_count': 50000},
    'mpumalanga': {'name': 'Mpumalanga', 'priority': 'HIGH', 'farmers_count': 45000},
    'north_west': {'name': 'North West', 'priority': 'HIGH', 'farmers_count': 35000},
    'gauteng': {'name': 'Gauteng', 'priority': 'MEDIUM', 'farmers_count': 15000},
    'limpopo': {'name': 'Limpopo', 'priority': 'HIGH', 'farmers_count': 40000},
    'northern_cape': {'name': 'Northern Cape', 'priority': 'MEDIUM', 'farmers_count': 10000},
    'western_cape': {'name': 'Western Cape', 'priority': 'HIGH', 'farmers_count': 25000},
    'eastern_cape': {'name': 'Eastern Cape', 'priority': 'MEDIUM', 'farmers_count': 20000},
    'kwazulu_natal': {'name': 'KwaZulu-Natal', 'priority': 'HIGH', 'farmers_count': 60000}
}

def get_sns_topic_arn():
    """Get SNS topic ARN from SSM Parameter Store"""
    try:
        response = ssm_client.get_parameter(Name='/africlimate/sns/alerts-topic')
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Error getting SNS topic ARN: {e}")
        return None

def execute_athena_query(query, query_id):
    """Execute Athena query and wait for results"""
    try:
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': DATABASE_NAME},
            ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
        )
        
        query_execution_id = response['QueryExecutionId']
        logger.info(f"Started Athena query {query_id}: {query_execution_id}")
        
        # Wait for query to complete
        while True:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            
            if state == 'SUCCEEDED':
                logger.info(f"Query {query_id} completed successfully")
                break
            elif state in ['FAILED', 'CANCELLED']:
                error = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                logger.error(f"Query {query_id} failed: {error}")
                return None
            else:
                logger.info(f"Query {query_id} status: {state}")
                import time
                time.sleep(2)
        
        # Get results
        results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        return results_response['ResultSet']
        
    except ClientError as e:
        logger.error(f"Error executing Athena query {query_id}: {e}")
        return None

def analyze_precipitation_deficits():
    """Analyze 30-day precipitation deficits by province"""
    
    # SQL query to get 30-day precipitation totals by region
    query = f"""
    WITH monthly_precip AS (
        SELECT 
            date,
            precipitation,
            -- Approximate province mapping based on coordinates
            CASE 
                WHEN latitude BETWEEN -30 AND -26 AND longitude BETWEEN 24 AND 29 THEN 'free_state'
                WHEN latitude BETWEEN -26 AND -24 AND longitude BETWEEN 29 AND 32 THEN 'mpumalanga'
                WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 22 AND 27 THEN 'north_west'
                WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 27 AND 29 THEN 'gauteng'
                WHEN latitude BETWEEN -24 AND -22 AND longitude BETWEEN 28 AND 32 THEN 'limpopo'
                WHEN latitude BETWEEN -32 AND -28 AND longitude BETWEEN 18 AND 24 THEN 'northern_cape'
                WHEN latitude BETWEEN -34 AND -31 AND longitude BETWEEN 18 AND 23 THEN 'western_cape'
                WHEN latitude BETWEEN -31 AND -28 AND longitude BETWEEN 23 AND 30 THEN 'eastern_cape'
                WHEN latitude BETWEEN -30 AND -27 AND longitude BETWEEN 29 AND 33 THEN 'kwazulu_natal'
                ELSE 'other'
            END as province
        FROM chirps_monthly
        WHERE date >= date_add('day', -30, current_date)
          AND precipitation IS NOT NULL
    )
    SELECT 
        province,
        SUM(precipitation) as total_precipitation_30d,
        AVG(precipitation) as avg_daily_precipitation,
        COUNT(*) as data_points
    FROM monthly_precip
    WHERE province != 'other'
    GROUP BY province
    ORDER BY total_precipitation_30d ASC
    """
    
    results = execute_athena_query(query, "precipitation_analysis")
    
    if not results:
        logger.error("Failed to get precipitation analysis results")
        return []
    
    # Parse results
    precipitation_data = []
    rows = results['Rows'][1:]  # Skip header row
    
    for row in rows:
        data = [col.get('VarCharValue', '0') for col in row['Data']]
        if len(data) >= 4:
            province = data[0]
            total_precip = float(data[1]) if data[1] else 0
            avg_daily = float(data[2]) if data[2] else 0
            data_points = int(data[3]) if data[3] else 0
            
            precipitation_data.append({
                'province': province,
                'total_precipitation_30d': total_precip,
                'avg_daily_precipitation': avg_daily,
                'data_points': data_points,
                'threshold_met': total_precip < DROUGHT_THRESHOLD_MM,
                'severe_drought': total_precip < SEVERE_DROUGHT_THRESHOLD_MM
            })
    
    return precipitation_data

def generate_drought_alerts(precipitation_data):
    """Generate drought alerts based on precipitation analysis"""
    alerts = []
    
    for data in precipitation_data:
        province_info = PROVINCES.get(data['province'], {})
        
        if data['severe_drought'] and province_info.get('priority') == 'HIGH':
            alert = {
                'severity': 'SEVERE',
                'province': province_info.get('name', data['province']),
                'precipitation_mm': round(data['total_precipitation_30d'], 1),
                'deficit_percent': round((1 - data['total_precipitation_30d'] / DROUGHT_THRESHOLD_MM) * 100, 1),
                'farmers_affected': province_info.get('farmers_count', 0),
                'recommendation': 'Immediate irrigation required. Water rationing advised.',
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
            
        elif data['threshold_met'] and province_info.get('priority') in ['HIGH', 'MEDIUM']:
            alert = {
                'severity': 'MODERATE',
                'province': province_info.get('name', data['province']),
                'precipitation_mm': round(data['total_precipitation_30d'], 1),
                'deficit_percent': round((1 - data['total_precipitation_30d'] / DROUGHT_THRESHOLD_MM) * 100, 1),
                'farmers_affected': province_info.get('farmers_count', 0),
                'recommendation': 'Prepare irrigation systems. Monitor weather forecasts.',
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
    
    return alerts

def format_sms_message(alert):
    """Format alert as SMS message"""
    emoji = "🚨" if alert['severity'] == 'SEVERE' else "⚠️"
    
    message = f"""{emoji} DROUGHT ALERT
Province: {alert['province']}
30-Day Rainfall: {alert['precipitation_mm']}mm
Deficit: {alert['deficit_percent']}%
Farmers Affected: {alert['farmers_affected']:,}
Action: {alert['recommendation']}
Time: {alert['timestamp'][:10]}"""
    
    return message

def send_sns_alerts(alerts):
    """Send alerts via SNS"""
    topic_arn = get_sns_topic_arn()
    
    if not topic_arn:
        logger.error("Could not get SNS topic ARN")
        return False
    
    alerts_sent = 0
    
    for alert in alerts:
        try:
            message = format_sms_message(alert)
            subject = f"{alert['severity']} Drought Alert - {alert['province']}"
            
            response = sns_client.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject,
                MessageAttributes={
                    'severity': {
                        'DataType': 'String',
                        'StringValue': alert['severity']
                    },
                    'province': {
                        'DataType': 'String',
                        'StringValue': alert['province']
                    }
                }
            )
            
            logger.info(f"Alert sent for {alert['province']}: {response['MessageId']}")
            alerts_sent += 1
            
        except ClientError as e:
            logger.error(f"Failed to send alert for {alert['province']}: {e}")
    
    logger.info(f"Sent {alerts_sent} drought alerts")
    return alerts_sent > 0

def store_analysis_results(precipitation_data, alerts):
    """Store analysis results in S3 for dashboard"""
    s3_client = boto3.client('s3', region_name='af-south-1')
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    results = {
        'analysis_timestamp': datetime.now().isoformat(),
        'precipitation_data': precipitation_data,
        'alerts': alerts,
        'summary': {
            'provinces_analyzed': len(precipitation_data),
            'drought_conditions': len([a for a in alerts if a['severity'] == 'MODERATE']),
            'severe_droughts': len([a for a in alerts if a['severity'] == 'SEVERE']),
            'total_alerts': len(alerts)
        }
    }
    
    try:
        s3_client.put_object(
            Bucket='africlimate-analytics-lake',
            Key=f'extensions/processed/drought/drought_analysis_{timestamp}.json',
            Body=json.dumps(results, default=str),
            ContentType='application/json'
        )
        logger.info(f"Stored drought analysis results to S3")
        
    except ClientError as e:
        logger.error(f"Failed to store analysis results: {e}")

def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info("Starting Drought Early Warning Analysis")
    
    try:
        # Analyze precipitation deficits
        precipitation_data = analyze_precipitation_deficits()
        
        if not precipitation_data:
            logger.error("No precipitation data available for analysis")
            return {
                'statusCode': 500,
                'body': json.dumps('Error: No precipitation data available')
            }
        
        logger.info(f"Analyzed precipitation for {len(precipitation_data)} provinces")
        
        # Generate drought alerts
        alerts = generate_drought_alerts(precipitation_data)
        logger.info(f"Generated {len(alerts)} drought alerts")
        
        # Send alerts via SNS
        if alerts:
            send_sns_alerts(alerts)
        
        # Store results for dashboard
        store_analysis_results(precipitation_data, alerts)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Drought analysis completed',
                'provinces_analyzed': len(precipitation_data),
                'alerts_generated': len(alerts),
                'severe_alerts': len([a for a in alerts if a['severity'] == 'SEVERE'])
            })
        }
        
    except Exception as e:
        logger.error(f"Error in drought analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

if __name__ == "__main__":
    # For local testing
    class MockContext:
        function_name = "drought-analyzer-test"
        memory_limit_in_mb = 256
        remaining_time_in_millis = 300000
    
    # Test with mock event
    test_event = {}
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
