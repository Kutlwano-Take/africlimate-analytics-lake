#!/usr/bin/env python3
"""
Production-Ready Step Functions Setup - Dynamic account ID
"""

import boto3
import json
from datetime import datetime

# Configuration
AWS_REGION = 'af-south-1'
STATE_MACHINE_NAME = 'AfriClimate-Comprehensive-Platform'

def create_step_function_definition():
    """Create Step Functions state machine definition with dynamic account ID"""
    
    # Get account ID dynamically
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    state_machine_definition = {
        "Comment": "AfriClimate Analytics Lake - Comprehensive Climate Platform Orchestration",
        "StartAt": "DataIngestionCheck",
        "TimeoutSeconds": 3600,
        "States": {
            "DataIngestionCheck": {
                "Type": "Task",
                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-data-validator",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-drought-early-warning",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-drought-early-warning",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-water-security",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-water-security",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-ndvi-impact",
                                "ResultPath": "$.ndvi_analysis",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-community-adaptation",
                                "ResultPath": "$.community_analysis",
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
                                "Resource": f"arn:aws:lambda:af-south-1:{account_id}:function:africlimate-carbon-footprint",
                                "ResultPath": "$.carbon_analysis",
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
                "Type": "Pass",
                "Parameters": {
                    "execution_status": "completed",
                    "timestamp.$": "$$.State.EnteredTime",
                    "components_executed.$": "$.parallel_results"
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
    
    # State machine configuration
    state_machine_config = {
        'name': STATE_MACHINE_NAME,
        'definition': json.dumps(definition),
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
            definition=json.dumps(definition)
        )
        
        print(f"✅ State machine updated successfully")
        return response['stateMachineArn']
        
    except Exception as e:
        print(f"❌ Failed to create state machine: {e}")
        return None

def main():
    """Main Step Functions setup function"""
    
    print("🔄 AfriClimate Analytics Lake - Step Functions Setup (Production)")
    print("=" * 60)
    
    # Create state machine
    state_machine_arn = create_step_function()
    
    if state_machine_arn:
        print(f"\n🎉 Step Functions Setup Complete!")
        print(f"🔄 State Machine: {STATE_MACHINE_NAME}")
        print(f"🚀 Ready for automated execution!")
        
        print(f"\n📋 Next Steps:")
        print(f"1. 🧪 Test individual Lambda functions")
        print(f"2. 📊 Set up QuickSight dashboard")
        print(f"3. 📧 Confirm email subscriptions")
        print(f"4. 🔄 Test Step Functions workflow")
        
    else:
        print(f"\n❌ Step Functions setup failed. Check logs and retry.")

if __name__ == "__main__":
    main()
