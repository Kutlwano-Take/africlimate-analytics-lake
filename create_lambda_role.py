#!/usr/bin/env python3
"""
Create IAM Role for Lambda Functions
"""

import boto3
import json

def create_lambda_role():
    """Create IAM role for Lambda functions"""
    
    iam = boto3.client('iam')
    
    # Trust policy for Lambda
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
    
    try:
        # Create role
        response = iam.create_role(
            RoleName='AfriclimateExtensionsRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='IAM role for AfriClimate Analytics Lake Lambda functions'
        )
        
        print(f"✅ Created IAM role: AfriclimateExtensionsRole")
        print(f"   ARN: {response['Role']['Arn']}")
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonSNSFullAccess',
            'arn:aws:iam::aws:policy/AmazonAthenaFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        
        for policy_arn in policies:
            iam.attach_role_policy(RoleName='AfriclimateExtensionsRole', PolicyArn=policy_arn)
            print(f"✅ Attached policy: {policy_arn}")
        
        return response['Role']['Arn']
        
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"⚠️ Role AfriclimateExtensionsRole already exists")
        response = iam.get_role(RoleName='AfriclimateExtensionsRole')
        return response['Role']['Arn']
        
    except Exception as e:
        print(f"❌ Error creating role: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Creating IAM Role for Lambda Functions")
    print("=" * 50)
    
    role_arn = create_lambda_role()
    
    if role_arn:
        print(f"\n🎉 IAM Role ready!")
        print(f"🚀 Now run: python deploy_lambda_functions.py")
    else:
        print(f"\n❌ Failed to create IAM role")
