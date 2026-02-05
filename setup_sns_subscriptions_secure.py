#!/usr/bin/env python3
"""
Secure SNS Subscriptions Setup - Uses placeholder emails for demo
"""

import boto3
import json
import time

# Configuration
AWS_REGION = 'af-south-1'

# Demo stakeholder email addresses (placeholders for security)
STAKEHOLDER_EMAILS = {
    'drought_alerts': [
        'farmer.demo@example.com',
        'agriculture.demo@example.com', 
        'weather.demo@example.com',
        'redcross.demo@example.com'
    ],
    'water_security': [
        'water.demo@example.com',
        'dam.demo@example.com',
        'urban.demo@example.com',
        'emergency.demo@example.com'
    ],
    'community_alerts': [
        'community.demo@example.com',
        'settlement.demo@example.com',
        'disaster.demo@example.com',
        'humanitarian.demo@example.com'
    ],
    'biodiversity_alerts': [
        'conservation.demo@example.com',
        'biodiversity.demo@example.com',
        'wildlife.demo@example.com',
        'climate.demo@example.com'
    ],
    'sustainability_alerts': [
        'energy.demo@example.com',
        'eskom.demo@example.com',
        'carbon.demo@example.com',
        'renewable.demo@example.com'
    ]
}

def setup_sns_subscriptions():
    """Set up SNS subscriptions for all alert topics"""
    
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    
    print("📧 Setting up SNS Subscriptions (Demo Mode)...")
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
    
    print(f"\n🎉 Subscription Summary: {subscription_count} email subscriptions created")
    print("📬 Check your email and confirm all subscriptions!")
    print("🔒 NOTE: Using demo emails for security - replace with real emails in production")
    
    return subscription_count

def create_sns_message_templates():
    """Create message templates for different alert types"""
    
    templates = {
        'drought_alert': {
            'subject': '🚨 DROUGHT ALERT: {risk_level} RISK - {region}',
            'message': '''
🌾 AFRICLIMATE FARMER ALERT - {region}

📅 Date: {date}
📍 Area: {region}
🌧️ Rainfall: {rainfall}mm
📉 SPI Index: {spi}

🚨 DROUGHT STATUS: {drought_level}
⚠️ RISK LEVEL: {risk_level}

💡 RECOMMENDATION:
{recommendation}

📞 For detailed forecasts: https://africlimate-analytics.com/farmers
🔄 Reply STOP to unsubscribe

---
AfriClimate Analytics Lake | Real-time climate intelligence for African farmers
            '''
        },
        'water_security': {
            'subject': '💧 WATER SECURITY ALERT: {dam_name} - {risk_level}',
            'message': '''
🚨 URBAN WATER SECURITY ALERT

📍 Dam: {dam_name}
📊 Current Level: {capacity}%
💧 Risk Level: {risk_level}
⏰ Days Until Critical: {days_critical}

📈 ANALYSIS:
{analysis_summary}

🎯 RECOMMENDED ACTIONS:
{recommendations}

📞 Contact: {emergency_contact}

---
AfriClimate Water Security System | Protecting urban water resources
            '''
        },
        'community_alert': {
            'subject': '🏘️ COMMUNITY CLIMATE ALERT: {settlement} - {risk_level}',
            'message': '''
🚨 CLIMATE EMERGENCY ALERT - {settlement}

📍 Location: {settlement}
👥 Population Affected: {population:,} residents
⚠️ Risk Level: {risk_level}
🌪️ Primary Threats: {threats}

📋 IMMEDIATE ACTIONS:
{immediate_actions}

📞 EMERGENCY CONTACTS:
{emergency_contacts}

⏰ This alert requires immediate attention and action.

---
AfriClimate Community Adaptation System | Protecting vulnerable communities
            '''
        }
    }
    
    # Save templates to S3 for reference
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    for template_name, template in templates.items():
        key = f"sns-templates/{template_name}.json"
        
        s3_client.put_object(
            Bucket='africlimate-analytics-lake',
            Key=key,
            Body=json.dumps(template, indent=2),
            ContentType='application/json'
        )
        print(f"💾 Saved template: {template_name}")
    
    print("✅ SNS message templates saved to S3")

def main():
    """Main setup function"""
    
    print("🌍 AfriClimate Analytics Lake - SNS Setup (Secure)")
    print("=" * 50)
    
    # Set up subscriptions
    subscription_count = setup_sns_subscriptions()
    
    # Create message templates
    create_sns_message_templates()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. ✅ Check email and confirm {subscription_count} subscriptions")
    print(f"2. 🚀 Deploy Lambda functions")
    print(f"3. 📊 Set up QuickSight dashboard")
    print(f"4. 🔄 Test end-to-end pipeline")
    print(f"5. 🔐 Replace demo emails with real stakeholder emails")

if __name__ == "__main__":
    main()
