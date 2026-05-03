"""
Worker Lambda: Processes events from SQS queue.
Performs final action: store in DynamoDB, notify stakeholders, trigger remediation.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from logger import log_event
from idempotency import is_duplicate, mark_as_processed, get_cached_result
from constants import RISK_LEVEL_CRITICAL, RISK_LEVEL_HIGH

def lambda_handler(event, context):
    """
    Process events from SQS.
    
    Input: SQS records containing scored events
    Output: Processed events, stored and notified
    """
    request_id = getattr(context, "aws_request_id", None)
    if request_id is None:
        request_id = getattr(context, "request_id", None)
    successful_count = 0
    failed_count = 0
    
    # SQS sends records array
    records = event.get("Records", [])
    
    if not records:
        log_event(
            action="ProcessSQSBatch",
            status="SUCCESS",
            request_id=request_id,
            detail={"recordsProcessed": 0}
        )
        return {"statusCode": 200, "body": json.dumps({"message": "No records to process"})}
    
    log_event(
        action="ProcessSQSBatch",
        status="STARTED",
        request_id=request_id,
        detail={"recordCount": len(records)}
    )
    
    try:
        for record in records:
            try:
                # Parse SQS message
                message_body = json.loads(record["body"])
                event_id = message_body.get("detail", {}).get("eventId", "unknown")
                
                # Check for duplicates
                if is_duplicate(event_id):
                    cached = get_cached_result(event_id)
                    log_event(
                        action="ProcessEvent",
                        status="SKIPPED",
                        event_id=event_id,
                        request_id=request_id,
                        detail={"reason": "Duplicate event"}
                    )
                    successful_count += 1
                    continue
                
                # Process the event
                result = process_event(message_body, request_id)
                
                # Mark as processed
                mark_as_processed(event_id, result)
                
                successful_count += 1
                
            except Exception as e:
                failed_count += 1
                event_id = "unknown"
                try:
                    event_id = json.loads(record["body"]).get("detail", {}).get("eventId", "unknown")
                except:
                    pass
                
                log_event(
                    action="ProcessEvent",
                    status="FAILED",
                    event_id=event_id,
                    request_id=request_id,
                    error=str(e)
                )
        
        log_event(
            action="ProcessSQSBatch",
            status="SUCCESS",
            request_id=request_id,
            detail={"successful": successful_count, "failed": failed_count}
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "processed": successful_count,
                "failed": failed_count,
                "total": len(records)
            })
        }
        
    except Exception as e:
        log_event(
            action="ProcessSQSBatch",
            status="FAILED",
            request_id=request_id,
            error=str(e)
        )
        raise

def process_event(event, request_id):
    """
    Process individual event.
    
    Steps:
    1. Extract and validate
    2. Store in DynamoDB (or log for demo)
    3. Notify if critical/high risk
    4. Trigger remediation if needed
    """
    event_id = event.get("detail", {}).get("eventId", "unknown")
    risk_level = event.get("detail", {}).get("riskLevel", "UNKNOWN")
    
    log_event(
        action="ProcessEvent",
        status="STARTED",
        event_id=event_id,
        request_id=request_id,
        detail={"riskLevel": risk_level}
    )
    
    # Store event (in production: DynamoDB)
    # For now: just log it
    log_event(
        action="StoreEvent",
        status="SUCCESS",
        event_id=event_id,
        request_id=request_id,
        detail={"eventType": event.get("detail", {}).get("eventType")}
    )
    
    # Send notifications for critical/high risk
    if risk_level in [RISK_LEVEL_CRITICAL, RISK_LEVEL_HIGH]:
        notify_security_team(event, request_id)
    
    # Trigger remediation if needed
    if should_remediate(event):
        trigger_remediation(event, request_id)
    
    log_event(
        action="ProcessEvent",
        status="SUCCESS",
        event_id=event_id,
        request_id=request_id
    )
    
    return {"processed": True, "eventId": event_id}

def notify_security_team(event, request_id):
    """Send notification to security team for high-risk events."""
    event_id = event.get("detail", {}).get("eventId")
    risk_level = event.get("detail", {}).get("riskLevel")
    
    log_event(
        action="NotifySecurityTeam",
        status="SUCCESS",
        event_id=event_id,
        request_id=request_id,
        detail={"riskLevel": risk_level, "channel": "SNS"}
    )

def should_remediate(event):
    """Determine if automatic remediation should be triggered."""
    risk_level = event.get("detail", {}).get("riskLevel")
    event_type = event.get("detail", {}).get("eventType")
    
    # Auto-remediate critical unauthorized API calls
    if risk_level == RISK_LEVEL_CRITICAL and event_type == "UnauthorizedAPICall":
        return True
    
    # Auto-remediate root account access
    if event.get("detail", {}).get("user") == "root":
        return True
    
    return False

def trigger_remediation(event, request_id):
    """Trigger automatic remediation actions."""
    event_id = event.get("detail", {}).get("eventId")
    event_type = event.get("detail", {}).get("eventType")
    user = event.get("detail", {}).get("user")
    
    # Example remediation actions (all logged, not executed)
    actions = []
    
    if user == "root":
        actions.append("Disable root access keys")
        actions.append("Alert security team immediately")
    
    if event_type == "UnauthorizedAPICall":
        actions.append("Revoke temporary credentials")
        actions.append("Block source IP")
    
    log_event(
        action="TrigerRemediationAction",
        status="SUCCESS",
        event_id=event_id,
        request_id=request_id,
        detail={"actions": actions}
    )
