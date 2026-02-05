#!/usr/bin/env python3
"""
AfriClimate Analytics Lake - Step Functions Workflow
Orchestrates all 5 creative extensions in parallel processing
"""

import boto3
import json
from datetime import datetime

# Configuration
AWS_REGION = 'af-south-1'
STATE_MACHINE_NAME = 'AfriClimate-Comprehensive-Platform'

def create_step_function_definition():
    """Create Step Functions state machine definition"""
    
    state_machine_definition = {
        "Comment": "AfriClimate Analytics Lake - Comprehensive Climate Platform Orchestration",
        "StartAt": "DataIngestionCheck",
        "TimeoutSeconds": 3600,
        "States": {
            "DataIngestionCheck": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-data-validator",
                "Parameters": {
                    "validation_type": "new_data_check"
                },
                "ResultPath": "$.validation_result",
                "Next": "ParallelClimateAnalysis"
            },
            "ParallelClimateAnalysis": {
                "Type": "Parallel",
                "Branches": [
                    {
                        "StartAt": "DroughtEarlyWarning",
                        "States": {
                            "DroughtEarlyWarning": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-drought-early-warning",
                                "ResultPath": "$.drought_analysis",
                                "Next": "DroughtAlerts"
                            },
                            "DroughtAlerts": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.drought_analysis.alerts_generated",
                                        "NumericGreaterThan": 0,
                                        "Next": "SendDroughtAlerts"
                                    }
                                ],
                                "Default": "DroughtComplete"
                            },
                            "SendDroughtAlerts": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-alert-sender",
                                "Parameters": {
                                    "alert_type": "drought",
                                    "recipients.$": "$.drought_analysis.high_risk_regions"
                                },
                                "ResultPath": "$.drought_alerts_sent",
                                "Next": "DroughtComplete"
                            },
                            "DroughtComplete": {
                                "Type": "Pass",
                                "Result": {
                                    "status": "completed",
                                    "component": "drought_early_warning"
                                },
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "WaterSecurityAnalysis",
                        "States": {
                            "WaterSecurityAnalysis": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-water-security",
                                "ResultPath": "$.water_analysis",
                                "Next": "WaterRiskAssessment"
                            },
                            "WaterRiskAssessment": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.water_analysis.security_score",
                                        "NumericLessThan": 50,
                                        "Next": "WaterSecurityAlert"
                                    }
                                ],
                                "Default": "WaterComplete"
                            },
                            "WaterSecurityAlert": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-alert-sender",
                                "Parameters": {
                                    "alert_type": "water_security",
                                    "urgency": "high"
                                },
                                "ResultPath": "$.water_alerts_sent",
                                "Next": "WaterComplete"
                            },
                            "WaterComplete": {
                                "Type": "Pass",
                                "Result": {
                                    "status": "completed",
                                    "component": "water_security"
                                },
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "NDVIImpactAnalysis",
                        "States": {
                            "NDVIImpactAnalysis": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-ndvi-impact",
                                "ResultPath": "$.ndvi_analysis",
                                "Next": "BiodiversityRiskCheck"
                            },
                            "BiodiversityRiskCheck": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.ndvi_analysis.high_risk_areas",
                                        "NumericGreaterThan": 0,
                                        "Next": "ConservationAlerts"
                                    }
                                ],
                                "Default": "NDVIComplete"
                            },
                            "ConservationAlerts": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-alert-sender",
                                "Parameters": {
                                    "alert_type": "biodiversity",
                                    "stakeholders": ["sanparks", "conservation_ngos"]
                                },
                                "ResultPath": "$.conservation_alerts_sent",
                                "Next": "NDVIComplete"
                            },
                            "NDVIComplete": {
                                "Type": "Pass",
                                "Result": {
                                    "status": "completed",
                                    "component": "ndvi_impact_tracker"
                                },
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "CommunityAdaptationAnalysis",
                        "States": {
                            "CommunityAdaptationAnalysis": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-community-adaptation",
                                "ResultPath": "$.community_analysis",
                                "Next": "CommunityRiskCheck"
                            },
                            "CommunityRiskCheck": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.community_analysis.high_risk_settlements",
                                        "NumericGreaterThan": 0,
                                        "Next": "CommunityAlerts"
                                    }
                                ],
                                "Default": "CommunityComplete"
                            },
                            "CommunityAlerts": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-alert-sender",
                                "Parameters": {
                                    "alert_type": "community",
                                    "urgency": "immediate"
                                },
                                "ResultPath": "$.community_alerts_sent",
                                "Next": "CommunityComplete"
                            },
                            "CommunityComplete": {
                                "Type": "Pass",
                                "Result": {
                                    "status": "completed",
                                    "component": "community_adaptation"
                                },
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "CarbonFootprintAnalysis",
                        "States": {
                            "CarbonFootprintAnalysis": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-carbon-footprint",
                                "ResultPath": "$.carbon_analysis",
                                "Next": "SustainabilityCheck"
                            },
                            "SustainabilityCheck": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.carbon_analysis.sustainability_score",
                                        "NumericLessThan": 40,
                                        "Next": "SustainabilityAlerts"
                                    }
                                ],
                                "Default": "CarbonComplete"
                            },
                            "SustainabilityAlerts": {
                                "Type": "Task",
                                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-alert-sender",
                                "Parameters": {
                                    "alert_type": "sustainability",
                                    "stakeholders": ["policy_makers", "energy_sector"]
                                },
                                "ResultPath": "$.sustainability_alerts_sent",
                                "Next": "CarbonComplete"
                            },
                            "CarbonComplete": {
                                "Type": "Pass",
                                "Result": {
                                    "status": "completed",
                                    "component": "carbon_footprint"
                                },
                                "End": True
                            }
                        }
                    }
                ],
                "ResultPath": "$.parallel_results",
                "Next": "AggregateResults"
            },
            "AggregateResults": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-results-aggregator",
                "Parameters": {
                    "analysis_results.$": "$.parallel_results",
                    "validation_result.$": "$.validation_result"
                },
                "ResultPath": "$.aggregated_results",
                "Next": "UpdateDashboard"
            },
            "UpdateDashboard": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-dashboard-updater",
                "Parameters": {
                    "dashboard_data.$": "$.aggregated_results"
                },
                "ResultPath": "$.dashboard_update",
                "Next": "GenerateReports"
            },
            "GenerateReports": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-report-generator",
                "Parameters": {
                    "comprehensive_analysis.$": "$.aggregated_results"
                },
                "ResultPath": "$.reports_generated",
                "Next": "NotificationCheck"
            },
            "NotificationCheck": {
                "Type": "Choice",
                "Choices": [
                    {
                        "And": [
                            {
                                "Variable": "$.aggregated_results.critical_alerts",
                                "NumericGreaterThan": 0
                            },
                            {
                                "Variable": "$.dashboard_update.status",
                                "Equals": "success"
                            }
                        ],
                        "Next": "SendExecutiveSummary"
                    }
                ],
                "Default": "ProcessComplete"
            },
            "SendExecutiveSummary": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:af-south-1:ACCOUNT_ID:function:africlimate-executive-notifier",
                "Parameters": {
                    "summary_data.$": "$.aggregated_results",
                    "priority": "high"
                },
                "ResultPath": "$.executive_notification",
                "Next": "ProcessComplete"
            },
            "ProcessComplete": {
                "Type": "Pass",
                "Parameters": {
                    "execution_status": "completed",
                    "timestamp.$": "$$.State.EnteredTime",
                    "total_duration.$": "$$.State.EnteredTime"
                },
                "End": True
            }
        }
    }
    
    return state_machine_definition

def create_step_function():
    """Create and configure Step Functions state machine"""
    
    stepfunctions_client = boto3.client('stepfunctions', region_name=AWS_REGION)
    
    # Get account ID
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # Create state machine definition
    definition = create_step_function_definition()
    
    # Replace placeholder with actual account ID
    definition_str = json.dumps(definition)
    definition_str = definition_str.replace('ACCOUNT_ID', account_id)
    
    # State machine configuration
    state_machine_config = {
        'name': STATE_MACHINE_NAME,
        'definition': definition_str,
        'roleArn': f'arn:aws:iam::{account_id}:role/StepFunctionsExecutionRole',
        'tags': [
            {
                'key': 'Project',
                'value': 'AfriClimate-Analytics-Lake'
            },
            {
                'key': 'Component',
                'value': 'Orchestration-Workflow'
            },
            {
                'key': 'Created',
                'value': datetime.now().isoformat()
            }
        ]
    }
    
    try:
        # Create state machine
        response = stepfunctions_client.create_state_machine(**state_machine_config)
        
        print(f"✅ Step Functions State Machine Created:")
        print(f"   Name: {STATE_MACHINE_NAME}")
        print(f"   ARN: {response['stateMachineArn']}")
        
        return response['stateMachineArn']
        
    except stepfunctions_client.exceptions.StateMachineAlreadyExists:
        print(f"⚠️ State machine already exists. Updating...")
        
        # Update existing state machine
        response = stepfunctions_client.update_state_machine(
            stateMachineArn=f'arn:aws:states:{AWS_REGION}:{account_id}:stateMachine:{STATE_MACHINE_NAME}',
            definition=definition_str
        )
        
        print(f"✅ State machine updated successfully")
        return response['stateMachineArn']
        
    except Exception as e:
        print(f"❌ Failed to create state machine: {e}")
        return None

def create_execution_role():
    """Create IAM role for Step Functions execution"""
    
    iam_client = boto3.client('iam', region_name=AWS_REGION)
    
    # Trust policy for Step Functions
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    "arn:aws:lambda:*:*:function:africlimate-*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": [
                    "arn:aws:sns:*:*:africlimate-*"
                ]
            }
        ]
    }
    
    try:
        # Create role
        iam_client.create_role(
            RoleName='StepFunctionsExecutionRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Step Functions execution role for AfriClimate Analytics Lake'
        )
        
        # Attach permissions
        iam_client.put_role_policy(
            RoleName='StepFunctionsExecutionRole',
            PolicyName='AfriClimateStepFunctionsPolicy',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        print("✅ Step Functions execution role created successfully")
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("⚠️ Step Functions execution role already exists")
        
    except Exception as e:
        print(f"❌ Failed to create execution role: {e}")

def create_schedule_expression():
    """Create schedule for automated execution"""
    
    # Run daily at 6 AM SAST (4 AM UTC)
    schedule_expression = "cron(0 4 * * ? *)"
    
    print(f"📅 Schedule Expression: {schedule_expression}")
    print(f"   Daily execution at 6 AM SAST")
    
    return schedule_expression

def main():
    """Main Step Functions setup function"""
    
    print("🔄 AfriClimate Analytics Lake - Step Functions Setup")
    print("=" * 60)
    
    # Create execution role
    create_execution_role()
    
    # Create state machine
    state_machine_arn = create_step_function()
    
    # Create schedule
    schedule = create_schedule_expression()
    
    if state_machine_arn:
        print(f"\n🎉 Step Functions Setup Complete!")
        print(f"🔄 State Machine: {STATE_MACHINE_NAME}")
        print(f"📅 Schedule: Daily at 6 AM SAST")
        print(f"🚀 Ready for automated execution!")
        
        print(f"\n📋 Next Steps:")
        print(f"1. 🧪 Test state machine execution")
        print(f"2. 📊 Verify dashboard updates")
        print(f"3. 📧 Confirm alert delivery")
        print(f"4. 📈 Monitor execution logs")
        
    else:
        print(f"\n❌ Step Functions setup failed. Check logs and retry.")

if __name__ == "__main__":
    main()
