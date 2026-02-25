#!/usr/bin/env python3
"""
Deploy Drought Analyzer Lambda Function
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

def create_iam_role():
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
    
    # IAM policy for the Lambda function
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
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults"
                ],
                "Resource": "*"
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
                    "sns:Publish"
                ],
                "Resource": "arn:aws:sns:af-south-1:*:africlimate-alerts"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameter"
                ],
                "Resource": "arn:aws:ssm:af-south-1:*:parameter/africlimate/*"
            }
        ]
    }
    
    try:
        # Create role
        response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AfriClimate Drought Analyzer Lambda"
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName='AfriClimateDroughtAnalyzerPolicy',
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
     with open('drought_analyzer.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    try:
        # Get shared layer ARN
        ssm_client = boto3.client('ssm', region_name=REGION)
        layer_response = ssm_client.get_parameter(Name='/africlimate/lambda/shared-layer')
        layer_arn = layer_response['Parameter']['Value']
        
        response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Description='Analyzes precipitation deficits and sends drought alerts',
            Timeout=300,  # 5 minutes
            MemorySize=256,
            Layers=[layer_arn],
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
            response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
            return response['Configuration']['FunctionArn']
        else:
            print(f"❌ Error creating Lambda function: {e}")
            return None

def create_eventbridge_schedule(function_arn):
    """Create EventBridge schedule for daily execution"""
    events_client = boto3.client('events', region_name=REGION)
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    rule_name = f'{FUNCTION_NAME}-schedule'
    
    try:
        # Create EventBridge rule
        events_client.put_rule(
            Name=rule_name,
            ScheduleExpression=SCHEDULE_EXPRESSION,
            State='ENABLED',
            Description='Daily trigger for drought analysis at 6 AM UTC'
        )
        print(f"✅ Created EventBridge rule: {rule_name}")
        
        # Add Lambda as target
        events_client.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': '1',
                    'Arn': function_arn,
                    'RetryPolicy': {
                        'MaximumRetryAttempts': 2,
                        'MaximumEventAgeInSeconds': 300
                    }
                }
            ]
        )
        print("✅ Added Lambda as target to EventBridge rule")
        
        # Add permission for EventBridge to invoke Lambda
        lambda_client.add_permission(
            FunctionName=FUNCTION_NAME,
            StatementId='EventBridgeInvoke',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f"arn:aws:events:{REGION}:*:rule/{rule_name}"
        )
        print("✅ Added EventBridge permission to Lambda")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error creating EventBridge schedule: {e}")
        return False

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
            print(f"✅ Lambda test successful: {payload}")
            return True
        else:
            print(f"❌ Lambda test failed with status: {response['StatusCode']}")
            return False
            
    except ClientError as e:
        print(f"❌ Error testing Lambda function: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying AfriClimate Drought Analyzer")
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
    
    # Create EventBridge schedule
    if not create_eventbridge_schedule(function_arn):
        print("❌ Failed to create EventBridge schedule")
        return
    
    # Test the function
    test_lambda_function()
    
    print("\n" + "=" * 50)
    print("✅ Drought Analyzer Deployment Complete!")
    print(f"Function: {FUNCTION_NAME}")
    print(f"Schedule: Daily at 6 AM UTC")
    print("Next: Test with real precipitation data")

if __name__ == "__main__":
    main()
