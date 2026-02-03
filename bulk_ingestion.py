#!/usr/bin/env python3
"""
Bulk CHIRPS Data Ingestion Script
Downloads and uploads CHIRPS monthly rainfall data from DE Africa to S3
"""

import subprocess
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DE_AFRICA_BUCKET = 'deafrica-input-datasets'
DE_AFRICA_PREFIX = 'rainfall_chirps_monthly/'
TARGET_BUCKET = 'africlimate-analytics-lake'
TARGET_PREFIX = 'raw/chirps_monthly/'
REGION = 'af-south-1'

def run_command(cmd):
    """Execute shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Command succeeded: {cmd}")
            return True, result.stdout
        else:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        logger.error(f"Exception running command: {cmd}")
        logger.error(f"Exception: {str(e)}")
        return False, str(e)

def download_and_upload_file(filename):
    """Download single file from DE Africa and upload to target S3"""
    logger.info(f"Processing: {filename}")
    
    # Download from DE Africa
    download_cmd = f"aws s3 cp --region {REGION} --no-sign-request s3://{DE_AFRICA_BUCKET}/{DE_AFRICA_PREFIX}{filename} ./{filename}"
    success, output = run_command(download_cmd)
    
    if not success:
        logger.error(f"Failed to download: {filename}")
        return False
    
    # Upload to target S3
    upload_cmd = f"aws s3 cp ./{filename} s3://{TARGET_BUCKET}/{TARGET_PREFIX}"
    success, output = run_command(upload_cmd)
    
    if not success:
        logger.error(f"Failed to upload: {filename}")
        return False
    
    # Clean up local file
    try:
        os.remove(filename)
        logger.info(f"Cleaned up local file: {filename}")
    except Exception as e:
        logger.warning(f"Failed to clean up {filename}: {str(e)}")
    
    return True

def get_file_list():
    """Get list of CHIRPS files from DE Africa"""
    logger.info("Getting file list from DE Africa...")
    
    cmd = f"aws s3 ls --region {REGION} --no-sign-request s3://{DE_AFRICA_BUCKET}/{DE_AFRICA_PREFIX}"
    success, output = run_command(cmd)
    
    if not success:
        logger.error("Failed to get file list")
        return []
    
    # Parse filenames from output
    files = []
    for line in output.split('\n'):
        if '.tif' in line:
            parts = line.strip().split()
            if len(parts) >= 4:
                filename = parts[-1]
                if filename.endswith('.tif'):
                    files.append(filename)
    
    logger.info(f"Found {len(files)} TIFF files")
    return files

def main():
    """Main ingestion function"""
    logger.info("Starting bulk CHIRPS data ingestion")
    start_time = datetime.now()
    
    # Get file list
    files = get_file_list()
    if not files:
        logger.error("No files found to process")
        return
    
    # Process files
    successful = 0
    failed = 0
    
    for i, filename in enumerate(files, 1):
        logger.info(f"Progress: {i}/{len(files)}")
        
        if download_and_upload_file(filename):
            successful += 1
        else:
            failed += 1
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 50)
    logger.info("BULK INGESTION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total files processed: {len(files)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {(successful/len(files)*100):.1f}%")
    logger.info(f"Duration: {duration}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
