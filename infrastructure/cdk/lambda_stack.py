"""
Lambda functions for enrichment, scoring, and SQS message processing.
"""

import os
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_iam as iam,
)

class LambdaStack(cdk.Stack):
    
    def __init__(
        self,
        scope: cdk.App,
        construct_id: str,
        iam_stack,
        sqs_stack,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.iam_stack = iam_stack
        self.sqs_stack = sqs_stack
        
        # ========== Enricher Function ==========
        self.enricher_fn = lambda_.Function(
            self, "EnricherFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="enricher.lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("../../functions"),
            role=iam_stack.enricher_role,
            timeout=cdk.Duration.seconds(60),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "production"
            },
            tracing=lambda_.Tracing.ACTIVE,  # Enable X-Ray
            description="Enriches security events with context"
        )
        
        # ========== Scorer Function ==========
        self.scorer_fn = lambda_.Function(
            self, "ScorerFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="scorer.lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("../../functions"),
            role=iam_stack.scorer_role,
            timeout=cdk.Duration.seconds(60),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "production",
                "QUEUE_URL": sqs_stack.queue.queue_url
            },
            tracing=lambda_.Tracing.ACTIVE,
            description="Scores security event risk"
        )
        
        # ========== Worker Function (SQS Consumer) ==========
        self.worker_fn = lambda_.Function(
            self, "WorkerFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="worker.lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("../../functions"),
            role=iam_stack.worker_role,
            timeout=cdk.Duration.seconds(300),
            memory_size=1024,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "production",
                "QUEUE_URL": sqs_stack.queue.queue_url
            },
            tracing=lambda_.Tracing.ACTIVE,
            description="Processes events from SQS"
        )
        
        # Event source mapping: SQS to Lambda
        self.worker_fn.add_event_source(
            lambda_event_sources.SqsEventSource(
                sqs_stack.queue,
                batch_size=10,  # Process 10 messages at a time
                max_batching_window=cdk.Duration.seconds(5)
            )
        )
        
        # Outputs for other stacks
        cdk.CfnOutput(
            self, "EnricherFunctionArn",
            value=self.enricher_fn.function_arn,
            export_name="EnricherFunctionArn"
        )
        
        cdk.CfnOutput(
            self, "ScorerFunctionArn",
            value=self.scorer_fn.function_arn,
            export_name="ScorerFunctionArn"
        )
        
        cdk.CfnOutput(
            self, "WorkerFunctionArn",
            value=self.worker_fn.function_arn,
            export_name="WorkerFunctionArn"
        )
