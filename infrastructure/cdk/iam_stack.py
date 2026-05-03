"""
IAM roles and policies for the security event pipeline.
Implements least-privilege principle: each component has minimal required permissions.
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
)

class IAMStack(cdk.Stack):
    
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # ========== Lambda Execution Roles ==========
        
        # Enricher Lambda role
        self.enricher_role = iam.Role(
            self, "EnricherRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for Enricher Lambda function"
        )
        
        # Enricher: need to log to CloudWatch and trace with X-Ray
        self.enricher_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
        )
        self.enricher_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )

        # Scorer Lambda role
        self.scorer_role = iam.Role(
            self, "ScorerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for Scorer Lambda function"
        )
        
        self.scorer_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
        )
        self.scorer_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )
        self.scorer_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sqs:SendMessage"],
                resources=["*"],
            )
        )
        
        # Worker Lambda role
        self.worker_role = iam.Role(
            self, "WorkerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for Worker Lambda function (SQS consumer)"
        )
        
        self.worker_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
        )
        self.worker_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )
        self.worker_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:ChangeMessageVisibility",
                ],
                resources=["*"],
            )
        )
        
        # ========== EventBridge Role ==========
        
        self.eventbridge_role = iam.Role(
            self, "EventBridgeRole",
            assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
            description="Role for EventBridge to invoke Lambda and send to SQS"
        )
        
        cdk.CfnOutput(
            self, "EnricherRoleArn",
            value=self.enricher_role.role_arn,
            export_name="EnricherRoleArn"
        )
        
        cdk.CfnOutput(
            self, "ScorerRoleArn",
            value=self.scorer_role.role_arn,
            export_name="ScorerRoleArn"
        )
        
        cdk.CfnOutput(
            self, "WorkerRoleArn",
            value=self.worker_role.role_arn,
            export_name="WorkerRoleArn"
        )
