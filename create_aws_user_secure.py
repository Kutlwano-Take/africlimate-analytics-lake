#!/usr/bin/env python3
"""
Create AWS IAM User and Access Keys for AfriClimate Project - SECURE VERSION
"""

import boto3
import json
import sys

def create_iam_user():
    """Create IAM user with required permissions"""
    
    try:
        # Create IAM client
        iam = boto3.client('iam')
        
        # User details
        username = 'africlimate-deployer'
        
        print(f"🔧 Creating IAM user: {username}")
        
        # Create user
        try:
            iam.create_user(UserName=username)
            print(f"✅ User {username} created successfully")
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"⚠️ User {username} already exists")
        
        # Attach policies
        policies = [
            'AmazonS3FullAccess',
            'AWSLambda_FullAccess', 
            'AmazonSNSFullAccess',
            'AmazonAthenaFullAccess',
            'AWSGlueConsoleFullAccess'
        ]
        
        for policy in policies:
            try:
                iam.attach_user_policy(UserName=username, PolicyArn=f'arn:aws:iam::aws:policy/{policy}')
                print(f"✅ Attached policy: {policy}")
            except Exception as e:
                print(f"❌ Failed to attach {policy}: {e}")
        
        # Create access keys
        print(f"🔑 Creating access keys for {username}")
        
        response = iam.create_access_key(UserName=username)
        access_key = response['AccessKey']
        
        print(f"\n🎉 SUCCESS! Your AWS Credentials:")
        print(f"=" * 50)
        print(f"Access Key ID: {access_key['AccessKeyId']}")
        print(f"Secret Access Key: [REDACTED - Check AWS Console]")
        print(f"=" * 50)
        
        print(f"\n📋 IMPORTANT: Save these credentials securely!")
        print(f"🚀 Now run: aws configure")
        print(f"📍 Region: af-south-1")
        print(f"📄 Output: json")
        
        # Save secure version (without secret key)
        credentials = {
            'AccessKeyId': access_key['AccessKeyId'],
            'UserName': username,
            'Created': access_key['CreateDate'].isoformat(),
            'Note': 'Secret key available in AWS Console only'
        }
        
        with open('aws_credentials_public.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"\n💾 Public credentials saved to: aws_credentials_public.json")
        print(f"🔐 Secret key only available in AWS Console")
        
        return access_key['AccessKeyId'], "[REDACTED]"
        
    except Exception as e:
        print(f"❌ Error creating IAM user: {e}")
        print(f"\n🔧 Alternative: Create user manually in AWS Console")
        return None, None

def main():
    """Main function"""
    print("🌍 AfriClimate Analytics Lake - AWS Setup (Secure)")
    print("=" * 50)
    
    # Check if AWS is configured
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Current AWS identity: [REDACTED]")
    except Exception as e:
        print(f"❌ AWS not configured: {e}")
        print(f"\n🔧 First configure AWS with your root account:")
        print(f"aws configure")
        print(f"\nThen run this script again.")
        return
    
    # Create IAM user
    access_key_id, secret_key = create_iam_user()
    
    if access_key_id and secret_key:
        print(f"\n🚀 Ready to deploy AfriClimate extensions!")
        print(f"📋 Next steps:")
        print(f"1. aws configure")
        print(f"2. Enter the credentials from AWS Console")
        print(f"3. python deploy_lambda_functions.py")

if __name__ == "__main__":
    main()
