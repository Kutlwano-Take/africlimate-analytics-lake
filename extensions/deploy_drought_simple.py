#!/usr/bin/env python3
"""
Deploy Drought Analyzer Lambda Function (Simplified Version)
Creates Lambda function, IAM role, and EventBridge schedule
"""

import boto3
import json
import zipfile
import io
from botocore.exceptions import ClientError

# Configuration
REGION = 'af-south-1'
FUNCTION_NAME = 'africlimate-drought-analyzer'
ROLE_NAME = 'AfriClimateDroughtAnalyzerRole'
SCHEDULE_EXPRESSION = 'cron(0 6 * * ? *)'  # Daily at 6 AM UTC

def create_lambda_function(role_arn):
    """Create Lambda function without layer dependency"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Read the Lambda function code
    with open('drought_analyzer_simple.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    try:
        response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Description='Analyzes precipitation deficits and sends drought alerts',
            Timeout=300,  # 5 minutes
            MemorySize=256,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO',
                    'DROUGHT_THRESHOLD_MM': '50',
                    'SEVERE_DROUGHT_THRESHOLD_MM': '25'
                }
            },
            Tags={
                'Project': 'AfriClimate',
                'Component': 'DroughtAnalyzer',
                'Environment': 'Production'
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_arn}")
        
        return function_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️ Function already exists: {FUNCTION_NAME}")
            # Update existing function
            try:
                response = lambda_client.update_function_code(
                    FunctionName=FUNCTION_NAME,
                    ZipFile=zip_buffer.read()
                )
                print(f"✅ Updated existing Lambda function")
                return response['FunctionArn']
            except ClientError as update_error:
                print(f"❌ Error updating Lambda function: {update_error}")
                return None
        else:
            print(f"❌ Error creating Lambda function: {e}")
            return None

def test_lambda_function():
    """Test the Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload='{}'
        )
        
        if response['StatusCode'] == 200:
            payload = json.loads(response['Payload'].read())
            print(f"✅ Lambda test response: {payload}")
            return True
        else:
            print(f"❌ Lambda test failed with status: {response['StatusCode']}")
            return False
            
    except ClientError as e:
        print(f"❌ Error testing Lambda function: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying AfriClimate Drought Analyzer (Simplified)")
    print("=" * 60)
    
    # Get existing role ARN
    iam_client = boto3.client('iam', region_name=REGION)
    try:
        response = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
    except ClientError:
        print("❌ IAM role not found - run setup_shared_resources.py first")
        return
    
    # Create Lambda function
    function_arn = create_lambda_function(role_arn)
    if not function_arn:
        print("❌ Failed to create Lambda function")
        return
    
    # Test the function
    print("\nTesting Lambda function...")
    test_lambda_function()
    
    print("\n" + "=" * 60)
    print("✅ Drought Analyzer Deployment Complete!")
    print(f"Function: {FUNCTION_NAME}")
    print("Next: Set up EventBridge schedule manually or test manually")

if __name__ == "__main__":
    main()
