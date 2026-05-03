"""
Monitoring stack: CloudWatch dashboards, X-Ray, and alarms.
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_logs as logs,
)

class MonitoringStack(cdk.Stack):
    
    def __init__(
        self,
        scope: cdk.App,
        construct_id: str,
        lambda_stack,
        sqs_stack,
        eventbridge_stack,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        # ========== CloudWatch Dashboard ==========
        dashboard = cloudwatch.Dashboard(
            self, "SecurityEventDashboard",
            dashboard_name="SecurityEventPipeline"
        )
        
        # Lambda metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations",
                left=[
                    lambda_stack.enricher_fn.metric_invocations(
                        statistic="Sum",
                        label="Enricher Invocations"
                    ),
                    lambda_stack.scorer_fn.metric_invocations(
                        statistic="Sum",
                        label="Scorer Invocations"
                    ),
                    lambda_stack.worker_fn.metric_invocations(
                        statistic="Sum",
                        label="Worker Invocations"
                    )
                ]
            ),
            cloudwatch.GraphWidget(
                title="Lambda Duration (ms)",
                left=[
                    lambda_stack.enricher_fn.metric_duration(
                        statistic="Average",
                        label="Enricher Avg"
                    ),
                    lambda_stack.scorer_fn.metric_duration(
                        statistic="Average",
                        label="Scorer Avg"
                    ),
                    lambda_stack.worker_fn.metric_duration(
                        statistic="Average",
                        label="Worker Avg"
                    )
                ]
            ),
            cloudwatch.GraphWidget(
                title="Lambda Errors",
                left=[
                    lambda_stack.enricher_fn.metric_errors(
                        statistic="Sum",
                        label="Enricher Errors"
                    ),
                    lambda_stack.scorer_fn.metric_errors(
                        statistic="Sum",
                        label="Scorer Errors"
                    ),
                    lambda_stack.worker_fn.metric_errors(
                        statistic="Sum",
                        label="Worker Errors"
                    )
                ]
            )
        )
        
        # SQS metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="SQS Queue Depth",
                left=[
                    sqs_stack.queue.metric_approximate_number_of_messages_visible(
                        statistic="Average",
                        label="Queue Depth"
                    )
                ]
            ),
            cloudwatch.GraphWidget(
                title="SQS Message Age",
                left=[
                    sqs_stack.queue.metric_approximate_age_of_oldest_message(
                        statistic="Average",
                        label="Oldest Message Age (seconds)"
                    )
                ]
            ),
            cloudwatch.GraphWidget(
                title="DLQ Messages",
                left=[
                    sqs_stack.dlq.metric_approximate_number_of_messages_visible(
                        statistic="Sum",
                        label="DLQ Depth"
                    )
                ]
            )
        )
        
        # High queue depth alarm
        queue_depth_alarm = cloudwatch.Alarm(
            self, "HighQueueDepthAlarm",
            metric=sqs_stack.queue.metric_approximate_number_of_messages_visible(),
            threshold=100,
            evaluation_periods=2,
            alarm_name="SecurityEventQueue-HighDepth",
            alarm_description="Alert when SQS queue has >100 messages"
        )
        
        # Lambda error rate alarm
        enricher_error_alarm = cloudwatch.Alarm(
            self, "EnricherErrorAlarm",
            metric=lambda_stack.enricher_fn.metric_errors(),
            threshold=5,
            evaluation_periods=1,
            alarm_name="Enricher-HighErrorRate",
            alarm_description="Alert when Enricher has >5 errors per minute"
        )
        
        # DLQ messages alarm
        dlq_alarm = cloudwatch.Alarm(
            self, "DLQMessagesAlarm",
            metric=sqs_stack.dlq.metric_approximate_number_of_messages_visible(),
            threshold=10,
            evaluation_periods=1,
            alarm_name="SecurityEventQueue-DLQMessages",
            alarm_description="Alert when DLQ has messages"
        )
        
        # Outputs
        cdk.CfnOutput(
            self, "DashboardUrl",
            value=f"https://console.aws.amazon.com/cloudwatch/home#dashboards:name=SecurityEventPipeline"
        )
