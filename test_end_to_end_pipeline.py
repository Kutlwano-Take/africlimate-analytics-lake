#!/usr/bin/env python3
"""
End-to-End Pipeline Test for AfriClimate Analytics Lake
Tests all 5 creative extensions with real data
"""

import boto3
import json
import time
from datetime import datetime

# Configuration
AWS_REGION = 'af-south-1'

def test_lambda_function(function_name, test_event):
    """Test individual Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    
    try:
        print(f"🧪 Testing {function_name}...")
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print(f"✅ {function_name} - SUCCESS")
            print(f"   Response: {result.get('body', 'No body')}")
            return True
        else:
            print(f"❌ {function_name} - FAILED: {response['StatusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ {function_name} - ERROR: {e}")
        return False

def test_step_function():
    """Test Step Functions workflow"""
    
    stepfunctions_client = boto3.client('stepfunctions', region_name=AWS_REGION)
    
    try:
        print("🔄 Testing Step Functions workflow...")
        
        # Start execution
        response = stepfunctions_client.start_execution(
            stateMachineArn='arn:aws:states:af-south-1:701742813629:stateMachine:AfriClimate-Comprehensive-Platform',
            name=f"test-execution-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            input=json.dumps({
                "test_mode": True,
                "test_data": "real_data_integration"
            })
        )
        
        execution_arn = response['executionArn']
        print(f"✅ Step Functions started: {execution_arn}")
        
        # Wait for completion
        for i in range(30):  # Wait up to 5 minutes
            try:
                result = stepfunctions_client.describe_execution(
                    executionArn=execution_arn
                )
                
                status = result['status']
                print(f"   Status: {status}")
                
                if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
                    break
                    
                time.sleep(10)
                
            except Exception as e:
                print(f"   Error checking status: {e}")
                break
        
        return status == 'SUCCEEDED'
        
    except Exception as e:
        print(f"❌ Step Functions test failed: {e}")
        return False

def test_sns_topics():
    """Test SNS topics are accessible"""
    
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    
    try:
        print("📧 Testing SNS topics...")
        
        topics = [
            'africlimate-drought-alerts',
            'africlimate-water-security',
            'africlimate-community-alerts',
            'africlimate-biodiversity-alerts',
            'africlimate-sustainability-alerts'
        ]
        
        for topic_name in topics:
            try:
                response = sns_client.list_topics()
                
                topic_found = False
                for topic in response['Topics']:
                    if topic_name in topic['TopicArn']:
                        print(f"✅ Found topic: {topic_name}")
                        topic_found = True
                        break
                
                if not topic_found:
                    print(f"❌ Topic not found: {topic_name}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking {topic_name}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ SNS test failed: {e}")
        return False

def test_athena_queries():
    """Test Athena queries can run"""
    
    athena_client = boto3.client('athena', region_name=AWS_REGION)
    
    try:
        print("🔍 Testing Athena queries...")
        
        # Test simple query
        query = "SELECT COUNT(*) as total_files FROM africlimate_climate_db.chirps_monthly_processed LIMIT 1"
        
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': 'africlimate_climate_db'},
            ResultConfiguration={'OutputLocation': 's3://africlimate-analytics-lake/athena-results/'}
        )
        
        query_execution_id = response['QueryExecutionId']
        print(f"✅ Athena query started: {query_execution_id}")
        
        # Wait for completion
        for i in range(20):  # Wait up to 3 minutes
            try:
                result = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
                status = result['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    print(f"✅ Athena query completed successfully")
                    return True
                elif status == 'FAILED':
                    print(f"❌ Athena query failed: {result['QueryExecution']['Status']['StateChangeReason']}")
                    return False
                
                time.sleep(10)
                
            except Exception as e:
                print(f"   Error checking query status: {e}")
                break
        
        print("⚠️ Athena query timed out")
        return False
        
    except Exception as e:
        print(f"❌ Athena test failed: {e}")
        return False

def test_s3_data_access():
    """Test S3 data access"""
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    try:
        print("🗂️ Testing S3 data access...")
        
        # Test bucket access
        response = s3_client.list_objects_v2(
            Bucket='africlimate-analytics-lake',
            Prefix='real-data/',
            MaxKeys=10
        )
        
        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} real data files")
            for obj in response['Contents'][:3]:
                print(f"   📁 {obj['Key']}")
            return True
        else:
            print("❌ No real data files found")
            return False
            
    except Exception as e:
        print(f"❌ S3 test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 AfriClimate Analytics Lake - End-to-End Pipeline Test")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: S3 Data Access
    test_results['s3_access'] = test_s3_data_access()
    
    # Test 2: Athena Queries
    test_results['athena_queries'] = test_athena_queries()
    
    # Test 3: SNS Topics
    test_results['sns_topics'] = test_sns_topics()
    
    # Test 4: Lambda Functions
    test_events = {
        'drought_early_warning': {
            'Records': [{
                's3': {
                    'bucket': {'name': 'africlimate-analytics-lake'},
                    'object': {'key': 'raw/chirps_monthly/year=2024/month=01/chirps-v2.0_2024.01.tif'}
                }
            }]
        },
        'africlimate-water-security': {
            'test_mode': True,
            'data_source': 'real_data'
        },
        'africlimate-ndvi-impact': {
            'test_mode': True,
            'data_source': 'real_data'
        },
        'africlimate-community-adaptation': {
            'test_mode': True,
            'data_source': 'real_data'
        },
        'africlimate-carbon-footprint': {
            'test_mode': True,
            'data_source': 'real_data'
        }
    }
    
    lambda_results = {}
    for function_name, test_event in test_events.items():
        lambda_results[function_name] = test_lambda_function(function_name, test_event)
    
    test_results['lambda_functions'] = all(lambda_results.values())
    
    # Test 5: Step Functions
    test_results['step_functions'] = test_step_function()
    
    # Summary
    print(f"\n🎉 Test Results Summary:")
    print(f"=" * 40)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED! Pipeline is fully operational!")
        print(f"🚀 Ready for production deployment!")
    else:
        print(f"⚠️ Some tests failed. Check logs and fix issues.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
