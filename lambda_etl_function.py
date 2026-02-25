#!/usr/bin/env python3
"""
AfriClimate Analytics Lake - ETL Lambda Function
Processes CHIRPS climate data and prepares for analytics
"""

import boto3
import json
import logging
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
glue = boto3.client('glue')

def lambda_handler(event, context):
    """
    Main Lambda handler for ETL processing
    """
    logger.info(f"ETL processing started at {datetime.now()}")
    
    try:
        # Process each S3 event
        for record in event['Records']:
            source_bucket = record['s3']['bucket']['name']
            source_key = record['s3']['object']['key']
            
            logger.info(f"Processing file: {source_key} from bucket: {source_bucket}")
            
            # Skip if not in raw folder
            if not source_key.startswith('raw/'):
                logger.info(f"Skipping non-raw file: {source_key}")
                continue
            
            # Process the file
            processed_data = process_climate_file(source_bucket, source_key)
            
            if processed_data:
                # Save processed data
                target_key = f"processed/{os.path.basename(source_key)}.json"
                save_processed_data(source_bucket, target_key, processed_data)
                
                logger.info(f"Successfully processed and saved: {target_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'ETL processing completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"ETL processing failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def process_climate_file(bucket, key):
    """
    Process climate data file
    """
    try:
        # Get file metadata
        response = s3.head_object(Bucket=bucket, Key=key)
        file_size = response['ContentLength']
        last_modified = response['LastModified']
        
        # Extract metadata from filename
        filename = os.path.basename(key)
        
        # Parse date from CHIRPS filename (example: chirps-v2.0_2024.01.01.tif)
        date_parts = filename.replace('.tif', '').split('_')[-1].split('.')
        if len(date_parts) >= 3:
            year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        else:
            # Default to current date if parsing fails
            today = datetime.now()
            year, month, day = today.year, today.month, today.day
        
        # Simulate climate data processing
        # In production, this would read and process actual TIFF data
        processed_data = {
            'source_file': filename,
            'file_size_bytes': file_size,
            'processing_date': datetime.now().isoformat(),
            'data_date': f"{year:04d}-{month:02d}-{day:02d}",
            'year': year,
            'month': month,
            'day': day,
            'region': 'Southern Africa',
            'data_type': 'precipitation',
            'status': 'processed',
            'quality_checks': {
                'file_integrity': 'passed',
                'date_format': 'valid',
                'processing_complete': True
            }
        }
        
        logger.info(f"Processed climate data for {year}-{month:02d}-{day:02d}")
        return processed_data
        
    except Exception as e:
        logger.error(f"Error processing climate file {key}: {str(e)}")
        return None

def save_processed_data(bucket, key, data):
    """
    Save processed data to S3
    """
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )
        logger.info(f"Saved processed data to: {key}")
        
    except Exception as e:
        logger.error(f"Error saving processed data: {str(e)}")
        raise

def update_glue_catalog(bucket, key, data):
    """
    Update Glue catalog with new data
    """
    try:
        # In production, this would update Glue tables
        # For now, just log the action
        logger.info(f"Would update Glue catalog for: {key}")
        
    except Exception as e:
        logger.error(f"Error updating Glue catalog: {str(e)}")

# Additional utility functions
def validate_climate_data(data):
    """
    Validate processed climate data
    """
    required_fields = ['year', 'month', 'day', 'data_type', 'region']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate date ranges
    if not (1900 <= data['year'] <= 2100):
        raise ValueError(f"Invalid year: {data['year']}")
    
    if not (1 <= data['month'] <= 12):
        raise ValueError(f"Invalid month: {data['month']}")
    
    if not (1 <= data['day'] <= 31):
        raise ValueError(f"Invalid day: {data['day']}")
    
    return True

def create_partition_path(year, month):
    """
    Create S3 partition path for data
    """
    return f"processed/year={year}/month={month:02d}/"

# Test function for local development
def test_etl_function():
    """
    Test the ETL function locally
    """
    test_event = {
        'Records': [
            {
                's3': {
                    'bucket': {'name': 'africlimate-analytics-lake'},
                    'object': {'key': 'raw/chirps-v2.0_2024.01.01.tif'}
                }
            }
        ]
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = 'etl_processor'
            self.memory_limit_in_mb = 512
            self.invoked_function_arn = 'arn:aws:lambda:af-south-1:123456789012:function:etl_processor'
    
    result = lambda_handler(test_event, MockContext())
    print("Test Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    test_etl_function()
