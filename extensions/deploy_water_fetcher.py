#!/usr/bin/env python3
"""
Deploy Water Fetcher Lambda Function
Creates Lambda function for urban water security analysis
"""

import boto3
import json
import zipfile
import io
from botocore.exceptions import ClientError

# Configuration
REGION = 'af-south-1'
FUNCTION_NAME = 'africlimate-water-fetcher'
ROLE_NAME = 'AfriClimateWaterFetcherRole'

def create_iam_role():
    """Create IAM role for Water Fetcher Lambda function"""
    iam_client = boto3.client('iam', region_name=REGION)
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # IAM policy for the Water Fetcher Lambda function
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::africlimate-analytics-lake/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "secretsmanager:GetSecretValue"
                ],
                "Resource": "arn:aws:secretsmanager:af-south-1:*:secret:africlimate/api-keys/*"
            }
        ]
    }
    
    try:
        # Create role
        response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AfriClimate Water Fetcher Lambda"
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName='AfriClimateWaterFetcherPolicy',
            PolicyDocument=json.dumps(policy_document)
        )
        
        print("✅ Attached inline policy to role")
        
        # Wait for role to be ready
        import time
        time.sleep(10)
        
        return role_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️ Role already exists: {ROLE_NAME}")
            response = iam_client.get_role(RoleName=ROLE_NAME)
            return response['Role']['Arn']
        else:
            print(f"❌ Error creating IAM role: {e}")
            return None

def create_lambda_function(role_arn):
    """Create Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Read the Lambda function code
    with open('water_fetcher.py', 'r', encoding='utf-8') as f:
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
            Description='Fetches dam levels and correlates with rainfall for water security analysis',
            Timeout=300,  # 5 minutes
            MemorySize=256,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO',
                    'BUCKET_NAME': 'africlimate-analytics-lake'
                }
            },
            Tags={
                'Project': 'AfriClimate',
                'Component': 'WaterFetcher',
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
    print("🚀 Deploying AfriClimate Water Fetcher")
    print("=" * 50)
    
    # Create IAM role
    role_arn = create_iam_role()
    if not role_arn:
        print("❌ Failed to create IAM role")
        return
    
    # Create Lambda function
    function_arn = create_lambda_function(role_arn)
    if not function_arn:
        print("❌ Failed to create Lambda function")
        return
    
    # Test the function
    print("\nTesting Lambda function...")
    test_lambda_function()
    
    print("\n" + "=" * 50)
    print("✅ Water Fetcher Deployment Complete!")
    print(f"Function: {FUNCTION_NAME}")
    print("Next: Create water security dashboard in Metabase")

if __name__ == "__main__":
    main()
