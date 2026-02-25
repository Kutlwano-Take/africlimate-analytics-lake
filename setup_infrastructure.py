#!/usr/bin/env python3
"""
AfriClimate Analytics Lake - Infrastructure Setup Script
Sets up S3 bucket, Glue database, Lambda functions, and IAM roles
"""

import boto3
import json
import time

class AfriClimateInfrastructure:
    def __init__(self):
        self.region = 'af-south-1'
        self.bucket_name = 'africlimate-analytics-lake'
        self.db_name = 'africlimate_climate_db'
        
        # Initialize AWS clients
        self.s3 = boto3.client('s3', region_name=self.region)
        self.glue = boto3.client('glue', region_name=self.region)
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.iam = boto3.client('iam', region_name=self.region)
        
    def create_s3_bucket(self):
        """Create S3 bucket for climate data storage"""
        print("🪣 Creating S3 bucket...")
        
        try:
            self.s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            
            # Create folder structure
            folders = ['raw/', 'processed/', 'athena-results/']
            for folder in folders:
                self.s3.put_object(Bucket=self.bucket_name, Key=folder, Body='')
            
            print(f"✅ S3 bucket '{self.bucket_name}' created with folder structure")
            return True
            
        except Exception as e:
            if 'BucketAlreadyExists' in str(e):
                print(f"✅ S3 bucket '{self.bucket_name}' already exists")
                return True
            else:
                print(f"❌ Error creating S3 bucket: {e}")
                return False
    
    def create_glue_database(self):
        """Create Glue database for metadata catalog"""
        print("🗄️ Creating Glue database...")
        
        try:
            self.glue.create_database(
                DatabaseInput={
                    'Name': self.db_name,
                    'Description': 'AfriClimate Analytics Lake - Climate Data Catalog'
                }
            )
            print(f"✅ Glue database '{self.db_name}' created")
            return True
            
        except Exception as e:
            if 'AlreadyExistsException' in str(e):
                print(f"✅ Glue database '{self.db_name}' already exists")
                return True
            else:
                print(f"❌ Error creating Glue database: {e}")
                return False
    
    def create_lambda_role(self):
        """Create IAM role for Lambda functions"""
        print("👥 Creating Lambda execution role...")
        
        role_name = 'AfriClimateLambdaExecutionRole'
        
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
        
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "glue:GetDatabase",
                        "glue:GetTable",
                        "athena:StartQueryExecution",
                        "athena:GetQueryExecution",
                        "athena:GetQueryResults"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Create role
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Lambda execution role for AfriClimate Analytics Lake'
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach execution policy
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName='AfriClimateLambdaExecutionPolicy',
                PolicyDocument=json.dumps(execution_policy)
            )
            
            print(f"✅ Lambda role '{role_name}' created")
            return role_arn
            
        except Exception as e:
            if 'EntityAlreadyExists' in str(e):
                print(f"✅ Lambda role '{role_name}' already exists")
                return f"arn:aws:iam::701742813629:role/{role_name}"
            else:
                print(f"❌ Error creating Lambda role: {e}")
                return None
    
    def deploy_lambda_functions(self, role_arn):
        """Deploy Lambda functions for ETL processing"""
        print("⚡ Deploying Lambda functions...")
        
        # ETL Processor function
        etl_code = '''
import boto3
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # Process incoming S3 events
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Simple ETL logic - in production, this would process climate data
        print(f"Processing file: {key} from bucket: {bucket}")
        
        # Move to processed folder
        processed_key = f"processed/{key.split('/')[-1]}"
        s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=processed_key)
        
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'ETL processing complete'})
    }
'''
        
        try:
            # Create ETL processor function
            self.lambda_client.create_function(
                FunctionName='etl_processor',
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': etl_code},
                Description='ETL processor for climate data',
                Timeout=300,
                MemorySize=512
            )
            
            print("✅ Lambda function 'etl_processor' deployed")
            return True
            
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                print("✅ Lambda function 'etl_processor' already exists")
                return True
            else:
                print(f"❌ Error deploying Lambda function: {e}")
                return False
    
    def setup_complete(self):
        """Print setup completion message"""
        print("\n🎉 AfriClimate Analytics Lake Infrastructure Setup Complete!")
        print("=" * 60)
        print("✅ S3 Bucket: Created for climate data storage")
        print("✅ Glue Database: Ready for metadata cataloging")
        print("✅ Lambda Functions: Deployed for ETL processing")
        print("✅ IAM Roles: Configured for secure access")
        print("\n🌐 Next Steps:")
        print("1. Upload CHIRPS data to S3://africlimate-analytics-lake/raw/")
        print("2. Configure Glue crawler for data cataloging")
        print("3. Set up Athena queries for analytics")
        print("4. Deploy Metabase for visualization")
        print("\n🚀 Your climate intelligence platform is ready!")

def main():
    """Main setup function"""
    print("🌍 AfriClimate Analytics Lake - Infrastructure Setup")
    print("=" * 60)
    
    infrastructure = AfriClimateInfrastructure()
    
    # Setup components
    s3_success = infrastructure.create_s3_bucket()
    if not s3_success:
        return
    
    glue_success = infrastructure.create_glue_database()
    if not glue_success:
        return
    
    role_arn = infrastructure.create_lambda_role()
    if not role_arn:
        return
    
    lambda_success = infrastructure.deploy_lambda_functions(role_arn)
    if not lambda_success:
        return
    
    # Complete setup
    infrastructure.setup_complete()

if __name__ == "__main__":
    main()
