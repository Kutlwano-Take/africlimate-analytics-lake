#!/usr/bin/env python3
"""
Setup Shared Resources for AfriClimate Extensions
Creates S3 folders, Lambda layers, SNS topics, and Secrets Manager entries
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

# AWS Configuration
REGION = 'af-south-1'
BUCKET_NAME = 'africlimate-analytics-lake'

def create_s3_folders():
    """Create extension-specific S3 folder structure"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    folders = [
        'extensions/raw/',
        'extensions/processed/',
        'extensions/raw/water/',
        'extensions/raw/ndvi/',
        'extensions/raw/community/',
        'extensions/raw/energy/',
        'extensions/processed/water/',
        'extensions/processed/ndvi/',
        'extensions/processed/community/',
        'extensions/processed/energy/'
    ]
    
    print("Creating S3 folder structure...")
    for folder in folders:
        try:
            s3_client.put_object(Bucket=BUCKET_NAME, Key=folder)
            print(f"✅ Created folder: {folder}")
        except ClientError as e:
            print(f"❌ Error creating {folder}: {e}")

def create_sns_topic():
    """Create SNS topic for alerts"""
    sns_client = boto3.client('sns', region_name=REGION)
    
    try:
        response = sns_client.create_topic(
            Name='africlimate-alerts',
            Attributes={
                'DisplayName': 'AfriClimate Alert System'
            }
        )
        topic_arn = response['TopicArn']
        print(f"✅ Created SNS topic: {topic_arn}")
        
        # Store topic ARN for later use
        ssm_client = boto3.client('ssm', region_name=REGION)
        ssm_client.put_parameter(
            Name='/africlimate/sns/alerts-topic',
            Value=topic_arn,
            Type='String',
            Description='SNS topic ARN for climate alerts'
        )
        print("✅ Stored SNS topic ARN in SSM Parameter Store")
        
        return topic_arn
    except ClientError as e:
        print(f"❌ Error creating SNS topic: {e}")
        return None

def create_lambda_layer():
    """Create shared Lambda layer with common utilities"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Create layer content zip (simplified for demo)
    layer_content = """# Lambda layer utilities
import boto3
import requests
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetch_api_data(url, params=None, headers=None):
    '''Generic API fetcher with error handling'''
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API fetch error: {e}")
        return None

def store_to_s3(data, bucket, key, region='af-south-1'):
    '''Store data to S3'''
    s3 = boto3.client('s3', region_name=region)
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, default=str),
            ContentType='application/json'
        )
        logger.info(f"Stored data to s3://{bucket}/{key}")
        return True
    except Exception as e:
        logger.error(f"S3 storage error: {e}")
        return False

def send_sns_alert(message, topic_arn, region='af-south-1'):
    '''Send alert via SNS'''
    sns = boto3.client('sns', region_name=region)
    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="AfriClimate Alert"
        )
        logger.info(f"Alert sent: {message}")
        return True
    except Exception as e:
        logger.error(f"SNS alert error: {e}")
        return False
"""
    
    # Create zip file (simplified - in production, use proper zip creation)
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('lambda_utils.py', layer_content)
    
    zip_buffer.seek(0)
    
    try:
        response = lambda_client.publish_layer_version(
            LayerName='africlimate-shared-utils',
            Description='Shared utilities for AfriClimate extensions',
            Content={'ZipFile': zip_buffer.read()},
            CompatibleRuntimes=['python3.8', 'python3.9'],
            LicenseInfo='MIT'
        )
        
        layer_arn = response['LayerArn']
        print(f"✅ Created Lambda layer: {layer_arn}")
        
        # Store layer ARN
        ssm_client = boto3.client('ssm', region_name=REGION)
        ssm_client.put_parameter(
            Name='/africlimate/lambda/shared-layer',
            Value=layer_arn,
            Type='String',
            Description='Lambda layer ARN for shared utilities'
        )
        
        return layer_arn
    except ClientError as e:
        print(f"❌ Error creating Lambda layer: {e}")
        return None

def setup_secrets_manager():
    """Setup Secrets Manager for API keys"""
    secrets_client = boto3.client('secretsmanager', region_name=REGION)
    
    secrets = {
        'africlimate/api-keys/dws': {
            'Description': 'Department of Water and Sanitation API keys',
            'SecretString': json.dumps({
                'api_key': 'your-dws-api-key-here',
                'base_url': 'https://www.dws.gov.za/Hydrology/Weekly/'
            })
        },
        'africlimate/api-keys/deafrica': {
            'Description': 'Digital Earth Africa API keys',
            'SecretString': json.dumps({
                'api_key': 'your-deafrica-api-key-here',
                'base_url': 'https://services.digitalearthafrica.org'
            })
        },
        'africlimate/api-keys/eskom': {
            'Description': 'Eskom energy data API keys',
            'SecretString': json.dumps({
                'api_key': 'your-eskom-api-key-here',
                'base_url': 'https://www.eskom.co.za/api'
            })
        }
    }
    
    print("Setting up Secrets Manager entries...")
    for secret_name, config in secrets.items():
        try:
            secrets_client.create_secret(
                Name=secret_name,
                Description=config['Description'],
                SecretString=config['SecretString']
            )
            print(f"✅ Created secret: {secret_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                print(f"⚠️ Secret already exists: {secret_name}")
            else:
                print(f"❌ Error creating secret {secret_name}: {e}")

def test_connectivity():
    """Test basic AWS connectivity"""
    print("\nTesting AWS connectivity...")
    try:
        # Test S3
        s3 = boto3.client('s3', region_name=REGION)
        buckets = s3.list_buckets()
        print(f"✅ S3 connected - Found {len(buckets['Buckets'])} buckets")
        
        # Test Lambda
        lambda_client = boto3.client('lambda', region_name=REGION)
        functions = lambda_client.list_functions(MaxItems=1)
        print("✅ Lambda connected")
        
        # Test Glue
        glue = boto3.client('glue', region_name=REGION)
        databases = glue.get_databases(MaxResults=1)
        print("✅ Glue connected")
        
        print("✅ All AWS services accessible")
        return True
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up AfriClimate Extensions Shared Resources")
    print("=" * 60)
    
    if not test_connectivity():
        print("❌ Cannot proceed - AWS connectivity issues")
        return
    
    create_s3_folders()
    sns_topic = create_sns_topic()
    lambda_layer = create_lambda_layer()
    setup_secrets_manager()
    
    print("\n" + "=" * 60)
    print("✅ Shared Resources Setup Complete!")
    print(f"SNS Topic: {sns_topic}")
    print(f"Lambda Layer: {lambda_layer}")
    print("S3 folders created for all extensions")
    print("Secrets Manager entries ready for API keys")
    print("\nNext: Implement Extension 1 - Drought Early Warning System")

if __name__ == "__main__":
    main()
