#!/usr/bin/env python3
"""
Test Email Subscriptions for AfriClimate Analytics Lake
"""

import boto3
import json
import time

# Configuration
AWS_REGION = 'af-south-1'

def test_sns_publish():
    """Test SNS message publishing"""
    
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    
    try:
        print("📧 Testing SNS message publishing...")
        
        # Test message
        test_message = """
🧪 AFRICLIMATE TEST MESSAGE

This is a test message from the AfriClimate Analytics Lake system.

📅 Date: 2026-02-05
🔧 System: Test Mode
✅ Status: All components operational

📞 If you receive this message, the alert system is working correctly.

---
AfriClimate Analytics Lake | Test Message
        """
        
        # Publish to all topics
        topics = [
            'africlimate-drought-alerts',
            'africlimate-water-security',
            'africlimate-community-alerts',
            'africlimate-biodiversity-alerts',
            'africlimate-sustainability-alerts'
        ]
        
        published_count = 0
        
        for topic_name in topics:
            try:
                # Get topic ARN
                response = sns_client.list_topics()
                topic_arn = None
                
                for topic in response['Topics']:
                    if topic_name in topic['TopicArn']:
                        topic_arn = topic['TopicArn']
                        break
                
                if topic_arn:
                    # Publish test message
                    response = sns_client.publish(
                        TopicArn=topic_arn,
                        Subject=f"🧪 AfriClimate Test - {topic_name.replace('-', ' ').title()}",
                        Message=test_message,
                        MessageAttributes={
                            'test_mode': {
                                'DataType': 'String',
                                'StringValue': 'true'
                            }
                        }
                    )
                    
                    print(f"✅ Published test message to {topic_name}")
                    print(f"   Message ID: {response['MessageId']}")
                    published_count += 1
                    
                else:
                    print(f"❌ Topic not found: {topic_name}")
                    
            except Exception as e:
                print(f"❌ Failed to publish to {topic_name}: {e}")
        
        print(f"\n🎉 Test messages published: {published_count}/{len(topics)}")
        print(f"📬 Check your email for test messages!")
        
        return published_count == len(topics)
        
    except Exception as e:
        print(f"❌ SNS test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("📧 AfriClimate Analytics Lake - Email Subscription Test")
    print("=" * 60)
    
    success = test_sns_publish()
    
    if success:
        print(f"\n✅ Email alert system is working!")
        print(f"📬 Check your inbox for test messages")
        print(f"🎯 Next: Set up QuickSight dashboard")
    else:
        print(f"\n❌ Email system needs troubleshooting")

if __name__ == "__main__":
    main()
