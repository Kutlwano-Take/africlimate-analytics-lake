#!/usr/bin/env python3
"""
Deploy All AfriClimate Extensions
Deploys Lambda functions for all 5 creative extensions
"""

import boto3
import json
import zipfile
import io
from botocore.exceptions import ClientError

# Configuration
REGION = 'af-south-1'
BUCKET_NAME = 'africlimate-analytics-lake'

# Extension functions to deploy
EXTENSIONS = {
    'africlimate-climate-impact-tracker': {
        'file': 'climate_impact_tracker.py',
        'role': 'AfriClimateClimateImpactRole',
        'description': 'Analyzes NDVI vegetation health with climate trends for conservation'
    },
    'africlimate-community-adaptation': {
        'file': 'community_adaptation_tool.py',
        'role': 'AfriClimateCommunityAdaptationRole',
        'description': 'Maps water access and vulnerability in informal settlements'
    },
    'africlimate-carbon-footprint': {
        'file': 'carbon_footprint_integration.py',
        'role': 'AfriClimateCarbonFootprintRole',
        'description': 'Tracks energy emissions with climate data for policy makers'
    }
}

def create_iam_role(role_name, description):
    """Create IAM role for Lambda function"""
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
    
    # Basic IAM policy for extension Lambda functions
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
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
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
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=f'{role_name}Policy',
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ Attached inline policy to {role_name}")
        
        # Wait for role to be ready
        import time
        time.sleep(10)
        
        return role_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️ Role already exists: {role_name}")
            response = iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        else:
            print(f"❌ Error creating IAM role {role_name}: {e}")
            return None

def create_lambda_function(function_name, file_name, role_arn, description):
    """Create Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Read the Lambda function code
    with open(file_name, 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Description=description,
            Timeout=300,
            MemorySize=256,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO',
                    'BUCKET_NAME': BUCKET_NAME
                }
            },
            Tags={
                'Project': 'AfriClimate',
                'Component': function_name.replace('africlimate-', ''),
                'Environment': 'Production'
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_name}")
        
        return function_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️ Function already exists: {function_name}")
            # Update existing function
            try:
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_buffer.read()
                )
                print(f"✅ Updated existing Lambda function: {function_name}")
                return response['FunctionArn']
            except ClientError as update_error:
                print(f"❌ Error updating Lambda function {function_name}: {update_error}")
                return None
        else:
            print(f"❌ Error creating Lambda function {function_name}: {e}")
            return None

def test_lambda_function(function_name):
    """Test the Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload='{}'
        )
        
        if response['StatusCode'] == 200:
            payload = json.loads(response['Payload'].read())
            print(f"✅ {function_name} test successful")
            return True
        else:
            print(f"❌ {function_name} test failed with status: {response['StatusCode']}")
            return False
            
    except ClientError as e:
        print(f"❌ Error testing {function_name}: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying All AfriClimate Extensions")
    print("=" * 60)
    
    deployed_functions = []
    
    for function_name, config in EXTENSIONS.items():
        print(f"\n--- Deploying {function_name} ---")
        
        # Create IAM role
        role_arn = create_iam_role(config['role'], config['description'])
        if not role_arn:
            print(f"❌ Failed to create IAM role for {function_name}")
            continue
        
        # Create Lambda function
        function_arn = create_lambda_function(
            function_name, 
            config['file'], 
            role_arn, 
            config['description']
        )
        if not function_arn:
            print(f"❌ Failed to create Lambda function {function_name}")
            continue
        
        deployed_functions.append(function_name)
    
    # Test all deployed functions
    print(f"\n--- Testing All Deployed Functions ---")
    successful_tests = 0
    
    for function_name in deployed_functions:
        if test_lambda_function(function_name):
            successful_tests += 1
    
    print("\n" + "=" * 60)
    print("✅ All Extensions Deployment Summary:")
    print(f"Functions deployed: {len(deployed_functions)}")
    print(f"Functions tested successfully: {successful_tests}")
    print(f"Functions with issues: {len(deployed_functions) - successful_tests}")
    
    if successful_tests == len(deployed_functions):
        print("🎉 All extensions are ready for production!")
    else:
        print("⚠️ Some extensions may need manual configuration")
    
    print("\nNext steps:")
    print("1. Create Metabase dashboards for each extension")
    print("2. Set up EventBridge schedules for automated execution")
    print("3. Configure SNS subscriptions for alerts")
    print("4. Update project documentation")

if __name__ == "__main__":
    main()
