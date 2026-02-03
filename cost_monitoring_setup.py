import boto3
import json
from datetime import datetime, timedelta

def setup_cloudwatch_monitoring():
    """
    Set up CloudWatch monitoring and alerts for cost optimization
    """
    cloudwatch = boto3.client('cloudwatch', region_name='af-south-1')
    
    # Create alarms for cost monitoring
    alarms = [
        {
            'AlarmName': 'Africlimate-Athena-Query-Cost-Alert',
            'AlarmDescription': 'Alert when Athena query costs exceed $0.05',
            'MetricName': 'QuerySucceeded',
            'Namespace': 'AWS/Athena',
            'Statistic': 'Sum',
            'Period': 86400,  # 24 hours
            'EvaluationPeriods': 1,
            'Threshold': 100,  # Adjust based on expected query volume
            'ComparisonOperator': 'GreaterThanThreshold',
            'TreatMissingData': 'notBreaching',
            'AlarmActions': [],  # Add SNS topic ARN if needed
            'Dimensions': [
                {
                    'Name': 'WorkGroup',
                    'Value': 'primary'
                }
            ]
        },
        {
            'AlarmName': 'Africlimate-Lambda-Invocation-Cost-Alert',
            'AlarmDescription': 'Alert when Lambda invocations exceed 1000 per day',
            'MetricName': 'Invocations',
            'Namespace': 'AWS/Lambda',
            'Statistic': 'Sum',
            'Period': 86400,  # 24 hours
            'EvaluationPeriods': 1,
            'Threshold': 1000,
            'ComparisonOperator': 'GreaterThanThreshold',
            'TreatMissingData': 'notBreaching',
            'AlarmActions': [],
            'Dimensions': [
                {
                    'Name': 'FunctionName',
                    'Value': 'africlimate-etl-function'
                }
            ]
        },
        {
            'AlarmName': 'Africlimate-S3-Storage-Cost-Alert',
            'AlarmDescription': 'Alert when S3 storage exceeds 4GB',
            'MetricName': 'BucketSizeBytes',
            'Namespace': 'AWS/S3',
            'Statistic': 'Average',
            'Period': 86400,  # 24 hours
            'EvaluationPeriods': 1,
            'Threshold': 4294967296,  # 4GB in bytes
            'ComparisonOperator': 'GreaterThanThreshold',
            'TreatMissingData': 'notBreaching',
            'AlarmActions': [],
            'Dimensions': [
                {
                    'Name': 'BucketName',
                    'Value': 'africlimate-analytics-lake'
                },
                {
                    'Name': 'StorageType',
                    'Value': 'StandardStorage'
                }
            ]
        }
    ]
    
    # Create each alarm
    for alarm_config in alarms:
        try:
            response = cloudwatch.put_metric_alarm(**alarm_config)
            print(f"Created alarm: {alarm_config['AlarmName']}")
        except Exception as e:
            print(f"Error creating alarm {alarm_config['AlarmName']}: {str(e)}")
    
    # Create custom metrics for cost tracking
    create_custom_metrics(cloudwatch)

def create_custom_metrics(cloudwatch):
    """
    Create custom metrics for detailed cost tracking
    """
    # Custom metric for ETL processing costs
    try:
        cloudwatch.put_metric_data(
            Namespace='Africlimate/ETL',
            MetricData=[
                {
                    'MetricName': 'ProcessingCost',
                    'Value': 0.0,
                    'Unit': 'None',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {
                            'Name': 'Service',
                            'Value': 'Lambda'
                        }
                    ]
                }
            ]
        )
        print("Created custom ETL cost metric")
    except Exception as e:
        print(f"Error creating custom metric: {str(e)}")

def create_cost_dashboard():
    """
    Create CloudWatch dashboard for cost monitoring
    """
    cloudwatch = boto3.client('cloudwatch', region_name='af-south-1')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Athena", "QuerySucceeded", "WorkGroup", "primary"],
                        [".", "QueryFailed", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "af-south-1",
                    "title": "Athena Query Activity",
                    "period": 3600
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", "FunctionName", "africlimate-etl-function"],
                        [".", "Errors", ".", "."],
                        [".", "Duration", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "af-south-1",
                    "title": "Lambda ETL Function Metrics",
                    "period": 3600
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/S3", "BucketSizeBytes", "BucketName", "africlimate-analytics-lake", "StorageType", "StandardStorage"],
                        [".", "NumberOfObjects", ".", ".", "StorageType", "AllStorageTypes"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "af-south-1",
                    "title": "S3 Storage Metrics",
                    "period": 86400
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["Africlimate/ETL", "ProcessingCost", "Service", "Lambda"],
                        [".", ".", "Service", "Athena"],
                        [".", ".", "Service", "Glue"]
                    ],
                    "view": "timeSeries",
                    "stacked": True,
                    "region": "af-south-1",
                    "title": "ETL Processing Costs by Service",
                    "period": 86400
                }
            }
        ]
    }
    
    try:
        response = cloudwatch.put_dashboard(
            DashboardName='Africlimate-Cost-Monitoring',
            DashboardBody=json.dumps(dashboard_body)
        )
        print("Created CloudWatch dashboard: Africlimate-Cost-Monitoring")
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")

def create_athena_workgroup():
    """
    Create dedicated Athena workgroup for cost control
    """
    athena = boto3.client('athena', region_name='af-south-1')
    
    workgroup_config = {
        'Name': 'africlimate-analytics',
        'Configuration': {
            'ResultConfiguration': {
                'OutputLocation': 's3://africlimate-analytics-lake/athena-results/'
            },
            'EnforceWorkGroupConfiguration': True,
            'PublishCloudWatchMetricsEnabled': True,
            'BytesScannedCutoffPerQuery': 1073741824,  # 1GB cutoff per query
            'RequesterPaysEnabled': False
        },
        'Description': 'Dedicated workgroup for Africlimate analytics with cost controls'
    }
    
    try:
        response = athena.create_work_group(**workgroup_config)
        print("Created Athena workgroup: africlimate-analytics")
    except Exception as e:
        print(f"Error creating workgroup: {str(e)}")

def setup_cost_optimization():
    """
    Main function to set up all cost optimization measures
    """
    print("Setting up CloudWatch monitoring and cost optimization...")
    
    # Set up monitoring
    setup_cloudwatch_monitoring()
    
    # Create dashboard
    create_cost_dashboard()
    
    # Create Athena workgroup
    create_athena_workgroup()
    
    print("Cost optimization setup completed!")

if __name__ == "__main__":
    setup_cost_optimization()
