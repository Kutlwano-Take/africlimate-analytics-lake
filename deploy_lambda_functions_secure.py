#!/usr/bin/env python3
"""
Secure Lambda Deployment Script - Uses environment variables instead of hardcoded account IDs
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

# Configuration
AWS_REGION = 'af-south-1'
LAMBDA_ROLE_NAME = 'AfriclimateExtensionsRole'
BUCKET_NAME = 'africlimate-analytics-lake'

# Initialize AWS clients
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
iam_client = boto3.client('iam', region_name=AWS_REGION)

# Get Lambda role ARN
def get_lambda_role_arn():
    try:
        response = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        return response['Role']['Arn']
    except Exception as e:
        print(f"Error getting role ARN: {e}")
        return None

# Create Lambda deployment package
def create_lambda_package(function_file, function_name):
    """Create ZIP package for Lambda function"""
    zip_filename = f"{function_name}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main function file
        zipf.write(function_file, f"{function_name}.py")
        
        # Add common dependencies
        dependencies = [
            'boto3',
            'pandas',
            'numpy',
            'pyarrow',
            'rasterio',
            'gdal'
        ]
        
        # Create requirements.txt
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join(dependencies))
        
        zipf.write('requirements.txt', 'requirements.txt')
    
    return zip_filename

# Deploy Lambda function
def deploy_lambda_function(function_name, handler_file, description, environment_vars=None):
    """Deploy Lambda function to AWS"""
    
    print(f"🚀 Deploying {function_name}...")
    
    # Create deployment package
    zip_file = create_lambda_package(handler_file, function_name)
    
    # Get role ARN
    role_arn = get_lambda_role_arn()
    if not role_arn:
        print(f"❌ Failed to get role ARN for {function_name}")
        return False
    
    # Get account ID dynamically
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # Lambda function configuration
    lambda_config = {
        'FunctionName': function_name,
        'Runtime': 'python3.9',
        'Role': role_arn,
        'Handler': f"{function_name}.lambda_handler",
        'Code': {
            'ZipFile': open(zip_file, 'rb').read()
        },
        'Description': description,
        'Timeout': 900,  # 15 minutes
        'MemorySize': 1024,  # 1GB
        'Environment': {
            'Variables': environment_vars or {}
        },
        'Tags': {
            'Project': 'AfriClimate-Analytics-Lake',
            'Component': function_name,
            'Created': datetime.now().isoformat()
        }
    }
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            # Update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=open(zip_file, 'rb').read()
            )
            print(f"✅ Updated {function_name}")
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = lambda_client.create_function(**lambda_config)
            print(f"✅ Created {function_name}")
        
        # Clean up zip file
        os.remove(zip_file)
        return True
        
    except Exception as e:
        print(f"❌ Failed to deploy {function_name}: {e}")
        if os.path.exists(zip_file):
            os.remove(zip_file)
        return False

# Main deployment function
def main():
    """Deploy all 5 creative extensions"""
    
    print("🌍 AfriClimate Analytics Lake - Lambda Deployment (Secure)")
    print("=" * 50)
    
    # Get account ID dynamically
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # Define Lambda functions to deploy
    lambda_functions = [
        {
            'name': 'africlimate-drought-early-warning',
            'file': 'drought_early_warning.py',
            'description': 'Drought Early Warning System for Farmers - Generates SNS alerts for drought conditions',
            'env_vars': {
                'SNS_TOPIC_ARN': f'arn:aws:sns:{AWS_REGION}:{account_id}:africlimate-drought-alerts',
                'ATHENA_DATABASE': 'africlimate_climate_db',
                'ATHENA_OUTPUT_LOCATION': f's3://{BUCKET_NAME}/athena-results/'
            }
        },
        {
            'name': 'africlimate-water-security',
            'file': 'urban_water_security.py',
            'description': 'Urban Water Security Dashboard - Analyzes dam levels vs rainfall correlations',
            'env_vars': {
                'ATHENA_DATABASE': 'africlimate_climate_db',
                'ATHENA_OUTPUT_LOCATION': f's3://{BUCKET_NAME}/athena-results/',
                'DAM_LEVELS_BUCKET': BUCKET_NAME,
                'DAM_LEVELS_PREFIX': 'external/water-dam-levels/'
            }
        },
        {
            'name': 'africlimate-ndvi-impact',
            'file': 'ndvi_climate_impact.py',
            'description': 'Climate Change Impact Tracker for Conservation - NDVI vegetation analysis',
            'env_vars': {
                'ATHENA_DATABASE': 'africlimate_climate_db',
                'ATHENA_OUTPUT_LOCATION': f's3://{BUCKET_NAME}/athena-results/',
                'NDVI_BUCKET': BUCKET_NAME,
                'NDVI_PREFIX': 'external/ndvi-data/'
            }
        },
        {
            'name': 'africlimate-community-adaptation',
            'file': 'community_adaptation_tool.py',
            'description': 'Community Climate Adaptation Tool - Risk assessments for informal settlements',
            'env_vars': {
                'ATHENA_DATABASE': 'africlimate_climate_db',
                'ATHENA_OUTPUT_LOCATION': f's3://{BUCKET_NAME}/athena-results/',
                'COMMUNITY_BUCKET': BUCKET_NAME,
                'COMMUNITY_PREFIX': 'community-adaptation/'
            }
        },
        {
            'name': 'africlimate-carbon-footprint',
            'file': 'carbon_footprint_integration.py',
            'description': 'Carbon Footprint Integration - Energy-climate correlation analysis',
            'env_vars': {
                'ATHENA_DATABASE': 'africlimate_climate_db',
                'ATHENA_OUTPUT_LOCATION': f's3://{BUCKET_NAME}/athena-results/',
                'CARBON_BUCKET': BUCKET_NAME,
                'CARBON_PREFIX': 'carbon-footprint/'
            }
        }
    ]
    
    # Deploy all functions
    deployed_count = 0
    for func in lambda_functions:
        if deploy_lambda_function(
            func['name'], 
            func['file'], 
            func['description'],
            func['env_vars']
        ):
            deployed_count += 1
    
    print(f"\n🎉 Deployment Summary: {deployed_count}/{len(lambda_functions)} functions deployed successfully")
    
    if deployed_count == len(lambda_functions):
        print("✅ All creative extensions deployed successfully!")
        print("🔥 Next: Set up SNS subscriptions and QuickSight dashboard")
    else:
        print("⚠️ Some deployments failed. Check logs and retry.")

if __name__ == "__main__":
    main()
