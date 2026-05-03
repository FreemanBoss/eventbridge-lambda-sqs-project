"""
SQS queues for event processing and dead-letter queue for failures.
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_sqs as sqs,
    aws_kms as kms,
)

class SQSStack(cdk.Stack):
    
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Dead-letter queue (DLQ) for messages that fail processing
        self.dlq = sqs.Queue(
            self, "SecurityEventDLQ",
            queue_name="SecurityEventQueue-DLQ",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.seconds(300),
            encryption=sqs.QueueEncryption.KMS_MANAGED,  # AWS managed key
            enforce_ssl=True
        )
        
        # Main event queue
        self.queue = sqs.Queue(
            self, "SecurityEventQueue",
            queue_name="SecurityEventQueue",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.seconds(300),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=2,  # Move to DLQ after 2 failed attempts
                queue=self.dlq
            ),
            encryption=sqs.QueueEncryption.KMS_MANAGED,
            enforce_ssl=True
        )
        
        # Outputs for other stacks
        cdk.CfnOutput(
            self, "QueueUrl",
            value=self.queue.queue_url,
            export_name="SecurityEventQueueUrl"
        )
        
        cdk.CfnOutput(
            self, "QueueArn",
            value=self.queue.queue_arn,
            export_name="SecurityEventQueueArn"
        )
        
        cdk.CfnOutput(
            self, "DLQUrl",
            value=self.dlq.queue_url,
            export_name="SecurityEventDLQUrl"
        )
        
        cdk.CfnOutput(
            self, "DLQArn",
            value=self.dlq.queue_arn,
            export_name="SecurityEventDLQArn"
        )
