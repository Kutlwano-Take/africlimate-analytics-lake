#!/bin/bash
# AfriClimate Analytics Lake - Deployment Script
# Creates all necessary AWS resources for 5 creative extensions

echo "🚀 Starting AfriClimate Analytics Lake Deployment..."

# Configuration
AWS_REGION="af-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="africlimate-analytics-lake"

# Create SNS Topics for Alerts
echo "📢 Creating SNS Topics..."
aws sns create-topic --name africlimate-drought-alerts --region $AWS_REGION
aws sns create-topic --name africlimate-water-security --region $AWS_REGION
aws sns create-topic --name africlimate-community-alerts --region $AWS_REGION
aws sns create-topic --name africlimate-biodiversity-alerts --region $AWS_REGION
aws sns create-topic --name africlimate-sustainability-alerts --region $AWS_REGION

# Create IAM Role for Lambda Functions
echo "🔐 Creating IAM Role for Extensions..."
cat > trust-policy.json << EOF
{
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
EOF

aws iam create-role --role-name AfriclimateExtensionsRole --assume-role-policy-document file://trust-policy.json --region $AWS_REGION

# Attach Policies
aws iam attach-role-policy --role-name AfriclimateExtensionsRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name AfriclimateExtensionsRole --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
aws iam attach-role-policy --role-name AfriclimateExtensionsRole --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess
aws iam attach-role-policy --role-name AfriclimateExtensionsRole --policy-arn arn:aws:iam::aws:policy/AmazonAthenaFullAccess

echo "✅ Infrastructure setup complete!"
