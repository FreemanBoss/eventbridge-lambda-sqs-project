"""
EventBridge custom event bus with routing rules for security events.
Routes events to Lambda functions (enricher, scorer) and SQS queue.
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
)

class EventBridgeStack(cdk.Stack):
    
    def __init__(
        self,
        scope: cdk.App,
        construct_id: str,
        lambda_stack,
        sqs_stack,
        iam_stack,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lambda_stack = lambda_stack
        self.sqs_stack = sqs_stack
        
        # ========== Custom Event Bus ==========
        self.event_bus = events.EventBus(
            self, "SecurityEventBus",
            event_bus_name="SecurityEventBus"
        )
        
        # ========== EventBridge Rules ==========
        
        # Rule 1: Route all events to Enricher
        enricher_rule = events.Rule(
            self, "SecurityEventEnricherRule",
            event_bus=self.event_bus,
            description="Route all security events to enricher",
            event_pattern=events.EventPattern(
                source=["custom.security"],
                detail_type=["Suspicious Activity"]
            )
        )
        
        enricher_rule.add_target(
            targets.LambdaFunction(
                lambda_stack.enricher_fn,
                max_event_age=cdk.Duration.minutes(5),
                retry_attempts=2
            )
        )
        
        # Rule 2: Route high-risk events to Scorer
        scorer_rule = events.Rule(
            self, "SecurityEventScorerRule",
            event_bus=self.event_bus,
            description="Route events to risk scorer",
            event_pattern=events.EventPattern(
                source=["custom.security"],
                detail_type=["Suspicious Activity"]
            )
        )

        scorer_rule.add_target(
            targets.LambdaFunction(
                lambda_stack.scorer_fn,
                max_event_age=cdk.Duration.minutes(5),
                retry_attempts=2
            )
        )

        # Outputs
        cdk.CfnOutput(
            self, "EventBusArn",
            value=self.event_bus.event_bus_arn,
            export_name="SecurityEventBusArn"
        )
        
        cdk.CfnOutput(
            self, "EventBusName",
            value=self.event_bus.event_bus_name,
            export_name="SecurityEventBusName"
        )
