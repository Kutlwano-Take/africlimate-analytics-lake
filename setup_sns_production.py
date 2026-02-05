#!/usr/bin/env python3
"""
Production-Ready SNS Subscriptions Setup - Environment variables for security
"""

import boto3
import json
import time
import os

# Configuration
AWS_REGION = 'af-south-1'

# Production stakeholder email addresses from environment variables
STAKEHOLDER_EMAILS = {
    'drought_alerts': [
        os.getenv('DROUGHT_EMAIL_1', 'farmer.demo@example.com'),
        os.getenv('DROUGHT_EMAIL_2', 'agriculture.demo@example.com'),
        os.getenv('DROUGHT_EMAIL_3', 'weather.demo@example.com'),
        os.getenv('DROUGHT_EMAIL_4', 'climate.demo@example.com'),
        os.getenv('DROUGHT_EMAIL_5', 'farmer.support.demo@example.com')
    ],
    'water_security': [
        os.getenv('WATER_EMAIL_1', 'water.demo@example.com'),
        os.getenv('WATER_EMAIL_2', 'dam.demo@example.com'),
        os.getenv('WATER_EMAIL_3', 'urban.demo@example.com'),
        os.getenv('WATER_EMAIL_4', 'emergency.demo@example.com'),
        os.getenv('WATER_EMAIL_5', 'randwater.demo@example.com')
    ],
    'community_alerts': [
        os.getenv('COMMUNITY_EMAIL_1', 'settlements.demo@example.com'),
        os.getenv('COMMUNITY_EMAIL_2', 'disaster.demo@example.com'),
        os.getenv('COMMUNITY_EMAIL_3', 'community.demo@example.com'),
        os.getenv('COMMUNITY_EMAIL_4', 'humanitarian.demo@example.com'),
        os.getenv('COMMUNITY_EMAIL_5', 'redcross.demo@example.com')
    ],
    'biodiversity_alerts': [
        os.getenv('BIODIVERSITY_EMAIL_1', 'research.demo@example.com'),
        os.getenv('BIODIVERSITY_EMAIL_2', 'biodiversity.demo@example.com'),
        os.getenv('BIODIVERSITY_EMAIL_3', 'conservation.demo@example.com'),
        os.getenv('BIODIVERSITY_EMAIL_4', 'birdlife.demo@example.com'),
        os.getenv('BIODIVERSITY_EMAIL_5', 'climate.demo@example.com')
    ],
    'sustainability_alerts': [
        os.getenv('SUSTAINABILITY_EMAIL_1', 'energy.demo@example.com'),
        os.getenv('SUSTAINABILITY_EMAIL_2', 'renewable.demo@example.com'),
        os.getenv('SUSTAINABILITY_EMAIL_3', 'climate.demo@example.com'),
        os.getenv('SUSTAINABILITY_EMAIL_4', 'carbon.demo@example.com'),
        os.getenv('SUSTAINABILITY_EMAIL_5', 'green.demo@example.com')
    ]
}

def setup_sns_subscriptions():
    """Set up SNS subscriptions for all alert topics"""
    
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    
    print("📧 Setting up SNS Subscriptions (Production Mode)...")
    print("=" * 40)
    
    subscription_count = 0
    
    for topic_name, emails in STAKEHOLDER_EMAILS.items():
        # Get topic ARN
        try:
            response = sns_client.create_topic(Name=f"africlimate-{topic_name}")
            topic_arn = response['TopicArn']
            print(f"📢 Topic: {topic_name}")
            
            # Subscribe each email
            for email in emails:
                try:
                    subscription = sns_client.subscribe(
                        TopicArn=topic_arn,
                        Protocol='email',
                        Endpoint=email
                    )
                    print(f"  ✅ Subscribed: {email}")
                    subscription_count += 1
                    
                    # Wait a bit to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ❌ Failed to subscribe {email}: {e}")
            
            print()
            
        except Exception as e:
            print(f"❌ Failed to create topic {topic_name}: {e}")
    
    print(f"\n🎉 Subscription Summary: {subscription_count} subscriptions created")
    print("📬 Check your email and confirm all subscriptions!")
    
    return subscription_count

def main():
    """Main setup function"""
    
    print("🌍 AfriClimate Analytics Lake - SNS Setup (Production)")
    print("=" * 50)
    
    # Set up subscriptions
    subscription_count = setup_sns_subscriptions()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. ✅ Check email and confirm {subscription_count} subscriptions")
    print(f"2. 🚀 Deploy Lambda functions")
    print(f"3. 📊 Set up QuickSight dashboard")
    print(f"4. 🔄 Test end-to-end pipeline")
    print(f"5. 🔐 Security scan before GitHub commit")

if __name__ == "__main__":
    main()
