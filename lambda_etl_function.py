import json
import boto3
import rasterio
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from rasterio.transform import from_bounds
from datetime import datetime
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
S3_CLIENT = boto3.client('s3')
PROCESSED_BUCKET = 'africlimate-analytics-lake'
PROCESSED_PREFIX = 'processed/enriched_climate/'

# Southern Africa bounding box
LAT_MIN, LAT_MAX = -35, -22
LON_MIN, LON_MAX = 16, 33

def lambda_handler(event, context):
    """
    Lambda ETL function for CHIRPS climate data processing
    Converts COG to Parquet and calculates climate metrics
    """
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Extract S3 event information
        for record in event['Records']:
            if record['eventSource'] == 'aws:s3':
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                # Only process CHIRPS files
                if not object_key.endswith('.tif'):
                    logger.info(f"Skipping non-TIFF file: {object_key}")
                    continue
                
                logger.info(f"Processing file: s3://{bucket_name}/{object_key}")
                
                # Process the file
                result = process_chirps_file(bucket_name, object_key)
                
                if result:
                    logger.info(f"Successfully processed {object_key}")
                else:
                    logger.error(f"Failed to process {object_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'ETL processing completed'})
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_chirps_file(bucket_name, object_key):
    """
    Process individual CHIRPS file: convert to Parquet and calculate metrics
    """
    try:
        # Extract date from filename
        filename = os.path.basename(object_key)
        year, month = extract_date_from_filename(filename)
        
        # Download file temporarily
        temp_file = f"/tmp/{filename}"
        S3_CLIENT.download_file(bucket_name, object_key, temp_file)
        
        # Process with rasterio
        with rasterio.open(temp_file) as src:
            # Read precipitation data
            precipitation_data = src.read(1)
            
            # Get coordinates
            bounds = src.bounds
            transform = src.transform
            
            # Create coordinate grids
            height, width = precipitation_data.shape
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            lons, lats = rasterio.transform.xy(transform, rows, cols)
            
            # Filter to Southern Africa region
            mask = ((lats >= LAT_MIN) & (lats <= LAT_MAX) & 
                   (lons >= LON_MIN) & (lons <= LON_MAX))
            
            if np.any(mask):
                # Extract data for Southern Africa
                sa_lats = lats[mask]
                sa_lons = lons[mask]
                sa_precip = precipitation_data[mask]
                
                # Calculate climate metrics
                climate_metrics = calculate_climate_metrics(
                    sa_precip, sa_lats, sa_lons, year, month
                )
                
                # Convert to DataFrame
                df = pd.DataFrame(climate_metrics)
                
                # Save as Parquet
                save_to_parquet(df, year, month)
                
                logger.info(f"Processed {len(df)} data points for {year}-{month:02d}")
                return True
            else:
                logger.warning(f"No data points in Southern Africa region for {filename}")
                return False
                
    except Exception as e:
        logger.error(f"Error processing {object_key}: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def extract_date_from_filename(filename):
    """
    Extract year and month from CHIRPS filename
    Example: chirps-v2.0_2024.01.tif -> 2024, 1
    """
    try:
        # Remove extension and prefix
        base = filename.replace('.tif', '').replace('chirps-v2.0_', '')
        year, month = base.split('.')
        return int(year), int(month)
    except Exception as e:
        logger.error(f"Error parsing filename {filename}: {str(e)}")
        return None, None

def calculate_climate_metrics(precipitation, lats, lons, year, month):
    """
    Calculate climate metrics for precipitation data
    """
    metrics = []
    
    for i in range(len(precipitation)):
        precip_value = precipitation[i]
        lat = lats[i]
        lon = lons[i]
        
        # Basic metrics
        metrics.append({
            'year': year,
            'month': month,
            'latitude': lat,
            'longitude': lon,
            'precipitation_mm': float(precip_value) if precip_value >= 0 else 0.0,
            'region_code': 'SOUTHERN_AFRICA',
            'data_quality': 'VALID' if precip_value >= 0 else 'INVALID'
        })
    
    return metrics

def save_to_parquet(df, year, month):
    """
    Save DataFrame to Parquet with partitioning
    """
    try:
        # Create partitioned path
        partition_path = f"{PROCESSED_PREFIX}year={year}/month={month:02d}/"
        filename = f"chirps_enriched_{year}_{month:02d}.parquet"
        s3_key = f"{partition_path}{filename}"
        
        # Convert to PyArrow Table
        table = pa.Table.from_pandas(df, preserve_index=False)
        
        # Write to temporary file
        temp_file = f"/tmp/chirps_{year}_{month:02d}.parquet"
        pq.write_table(table, temp_file, compression='snappy')
        
        # Upload to S3
        S3_CLIENT.upload_file(temp_file, PROCESSED_BUCKET, s3_key)
        
        logger.info(f"Saved Parquet file: s3://{PROCESSED_BUCKET}/{s3_key}")
        
        # Clean up
        os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"Error saving Parquet: {str(e)}")
        raise

# Test function for local development
def test_local_processing():
    """
    Test function for local development
    """
    test_event = {
        'Records': [
            {
                'eventSource': 'aws:s3',
                's3': {
                    'bucket': {'name': 'africlimate-analytics-lake'},
                    'object': {'key': 'raw/chirps_monthly/chirps-v2.0_2024.01.tif'}
                }
            }
        ]
    }
    
    # Mock context
    class MockContext:
        pass
    
    return lambda_handler(test_event, MockContext())

if __name__ == "__main__":
    # For local testing
    test_local_processing()
