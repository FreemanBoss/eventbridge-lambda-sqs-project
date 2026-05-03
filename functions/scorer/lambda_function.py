"""
Scorer Lambda: Calculates risk score for security events.
Risk score: 0 (safe) to 100 (critical).
"""

import json
import sys
import os
import boto3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from logger import log_event
from constants import (
    EVENT_TYPE_WEIGHTS,
    RISK_THRESHOLD_CRITICAL,
    RISK_THRESHOLD_HIGH,
    RISK_THRESHOLD_MEDIUM,
    RISK_LEVEL_CRITICAL,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_LOW
)

sqs_client = boto3.client("sqs")

def lambda_handler(event, context):
    """
    Score security event for risk level.
    
    Input: Enriched event from EventBridge
    Output: Event with risk score and severity level
    """
    request_id = getattr(context, "aws_request_id", None)
    if request_id is None:
        request_id = getattr(context, "request_id", None)
    
    try:
        event_detail = event.get("detail", {})
        event_id = event_detail.get("eventId")
        
        log_event(
            action="ScoreEvent",
            status="STARTED",
            event_id=event_id,
            request_id=request_id
        )
        
        # Calculate risk score
        risk_score = calculate_risk_score(event_detail)
        risk_level = get_risk_level(risk_score)
        
        # Add scoring to event
        scored_event = event.copy()
        if "detail" not in scored_event:
            scored_event["detail"] = {}
        
        scored_event["detail"]["riskScore"] = risk_score
        scored_event["detail"]["riskLevel"] = risk_level
        scored_event["detail"]["scoredAt"] = __import__('datetime').datetime.utcnow().isoformat()

        queue_url = os.getenv("QUEUE_URL")
        if queue_url:
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(scored_event)
            )
        
        log_event(
            action="ScoreEvent",
            status="SUCCESS",
            event_id=event_id,
            request_id=request_id,
            detail={"riskScore": risk_score, "riskLevel": risk_level}
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps(scored_event)
        }
        
    except Exception as e:
        event_id = event.get("detail", {}).get("eventId", "unknown")
        log_event(
            action="ScoreEvent",
            status="FAILED",
            event_id=event_id,
            request_id=request_id,
            error=str(e)
        )
        raise

def calculate_risk_score(event_detail):
    """
    Calculate risk score based on event characteristics.
    Scoring factors:
      - Event type base weight: 0–1.0, scaled to 0–40 points
      - Failure indicator: 0–20 points
      - Rate limit indicator: 0–15 points
      - Multiple attempts: 0–15 points
      - Root account: 0–60 points
      - Geolocation surprise: 0–15 points
    Total: 0–100
    """
    score = 0.0
    
    # Event type base weight (40 points max)
    event_type = event_detail.get("eventType", "Unknown")
    base_weight = EVENT_TYPE_WEIGHTS.get(event_type, 0.5)
    score += base_weight * 40
    
    # Failure indicator (20 points)
    result = event_detail.get("result", "").upper()
    if result in ["FAIL", "FAILED"]:
        score += 20
    
    # Rate limit exceeded (15 points)
    if event_detail.get("rateLimitExceeded"):
        score += 15
    
    # Multiple failed attempts (15 points)
    attempt_count = event_detail.get("attemptCount", 1)
    if attempt_count > 2:
        score += 15
    
    # Root account access (60 points, critical)
    if event_detail.get("user") == "root":
        score += 60
    
    # Unusual geography (15 points)
    if is_unusual_geography(event_detail):
        score += 15
    
    # No MFA used for sensitive action (20 points)
    if not event_detail.get("mfaUsed") and event_detail.get("eventType") in ["IAMPolicyChange", "AccessKeyCreated"]:
        score += 20
    
    # Cap at 100
    return min(100, int(score))

def is_unusual_geography(event_detail):
    """Check if geography is unusual."""
    current_country = event_detail.get("country")
    previous_country = event_detail.get("previousLoginCountry")
    time_since_last = event_detail.get("timeSinceLastLogin", "")
    
    # Country change within short time = suspicious
    if current_country and previous_country and current_country != previous_country:
        if time_since_last and "h" in time_since_last:
            hours = int(time_since_last.replace("h", ""))
            if hours < 24:
                return True
    
    return False

def get_risk_level(score):
    """Get risk level name from score."""
    if score >= RISK_THRESHOLD_CRITICAL:
        return RISK_LEVEL_CRITICAL
    elif score >= RISK_THRESHOLD_HIGH:
        return RISK_LEVEL_HIGH
    elif score >= RISK_THRESHOLD_MEDIUM:
        return RISK_LEVEL_MEDIUM
    else:
        return RISK_LEVEL_LOW
