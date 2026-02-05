#!/usr/bin/env python3
"""
Quick SNS Topic Check and Test
"""

import boto3

def check_and_test_sns():
    """Check SNS topics and send test messages"""
    
    sns_client = boto3.client('sns', region_name='af-south-1')
    
    try:
        # List all topics
        response = sns_client.list_topics()
        
        print("📧 Current SNS Topics:")
        print("=" * 40)
        
        topic_arns = {}
        for topic in response['Topics']:
            topic_arn = topic['TopicArn']
            topic_name = topic_arn.split(':')[-1]
            topic_arns[topic_name] = topic_arn
            print(f"✅ {topic_name}")
        
        if not topic_arns:
            print("❌ No SNS topics found!")
            return False
        
        # Send test message to first topic
        first_topic = list(topic_arns.values())[0]
        first_name = list(topic_arns.keys())[0]
        
        print(f"\n🧪 Sending test message to: {first_name}")
        
        test_message = """
🧪 AFRICLIMATE TEST ALERT

This is a test message from the AfriClimate Analytics Lake.

📅 Date: 2026-02-05
🔧 System: Test Mode
✅ Status: Alert system working

---
AfriClimate Analytics Lake | Test System
        """
        
        response = sns_client.publish(
            TopicArn=first_topic,
            Subject=f"🧪 AfriClimate Test - {first_name}",
            Message=test_message
        )
        
        print(f"✅ Test message sent!")
        print(f"   Message ID: {response['MessageId']}")
        print(f"   Topic: {first_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_and_test_sns()
