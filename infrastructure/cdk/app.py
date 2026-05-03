#!/usr/bin/env python3
"""
Production-Grade Event-Driven Security Pipeline
AWS Cloud Security UserGroup Workshop

Main CDK Application orchestrator
"""

import os
import aws_cdk as cdk
from eventbridge_stack import EventBridgeStack
from lambda_stack import LambdaStack
from sqs_stack import SQSStack
from iam_stack import IAMStack
from monitoring_stack import MonitoringStack

def main():
    app = cdk.App()
    
    # Configuration
    env = cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    )
    
    project_name = "SecurityEventPipeline"

    # 1. IAM roles and policies
    iam_stack = IAMStack(
        app,
        f"{project_name}IAMStack",
        env=env,
        description="IAM roles for EventBridge, Lambda, and SQS"
    )
    
    # 2. SQS queues
    sqs_stack = SQSStack(
        app,
        f"{project_name}SQSStack",
        env=env,
        description="SQS queues for event processing"
    )
    
    # 3. Lambda functions
    lambda_stack = LambdaStack(
        app,
        f"{project_name}LambdaStack",
        env=env,
        iam_stack=iam_stack,
        sqs_stack=sqs_stack,
        description="Lambda functions for enrichment, scoring, and processing"
    )
    lambda_stack.add_dependency(iam_stack)
    lambda_stack.add_dependency(sqs_stack)
    
    # 4. EventBridge rules and routing
    eventbridge_stack = EventBridgeStack(
        app,
        f"{project_name}EventBridgeStack",
        env=env,
        lambda_stack=lambda_stack,
        sqs_stack=sqs_stack,
        iam_stack=iam_stack,
        description="EventBridge custom event bus with routing rules"
    )
    eventbridge_stack.add_dependency(lambda_stack)
    eventbridge_stack.add_dependency(sqs_stack)
    
    # 5. Monitoring (CloudWatch, X-Ray, Alarms)
    monitoring_stack = MonitoringStack(
        app,
        f"{project_name}MonitoringStack",
        env=env,
        lambda_stack=lambda_stack,
        sqs_stack=sqs_stack,
        eventbridge_stack=eventbridge_stack,
        description="CloudWatch dashboards, X-Ray, and alarms"
    )
    monitoring_stack.add_dependency(eventbridge_stack)
    
    # Tags for cost tracking
    cdk.Tags.of(app).add("Project", "SecurityEventPipeline")
    cdk.Tags.of(app).add("Workshop", "AWS-Cloud-Security-UserGroup")
    cdk.Tags.of(app).add("Date", "2026-05-02")
    
    app.synth()

if __name__ == "__main__":
    main()
