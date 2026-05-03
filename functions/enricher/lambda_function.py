"""
Enricher Lambda: Adds context to security events.
Enrichment includes: geolocation, account owner, user details, asset metadata.
"""

import json
import sys
import os

# Add shared functions to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from logger import log_event, get_request_id
from validator import validate_event, sanitize_event
from constants import EVENT_TYPE_WEIGHTS

def lambda_handler(event, context):
    """
    Main handler for enrichment Lambda.
    
    Input: Raw security event from EventBridge
    Output: Enriched event with additional context
    """
    request_id = getattr(context, "aws_request_id", None)
    if request_id is None:
        request_id = getattr(context, "request_id", None)
    
    try:
        # Extract event detail
        event_detail = event.get("detail", {})
        event_id = event_detail.get("eventId")
        
        # Validate event structure
        is_valid, errors = validate_event(event)
        if not is_valid:
            log_event(
                action="ValidateEvent",
                status="FAILED",
                event_id=event_id,
                request_id=request_id,
                error="; ".join(errors)
            )
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid event", "details": errors})
            }
        
        log_event(
            action="EnrichEvent",
            status="STARTED",
            event_id=event_id,
            request_id=request_id
        )
        
        # Enrich the event with context
        enriched_event = {
            "originalEvent": sanitize_event(event),
            "enrichment": {
                "requestId": request_id,
                "processedAt": __import__('datetime').datetime.utcnow().isoformat(),
                "enrichments": {
                    "geolocation": enrich_geolocation(event_detail),
                    "account": enrich_account(event_detail),
                    "user": enrich_user(event_detail),
                    "asset": enrich_asset(event_detail),
                    "threat_indicators": enrich_threat_indicators(event_detail)
                }
            }
        }
        
        log_event(
            action="EnrichEvent",
            status="SUCCESS",
            event_id=event_id,
            request_id=request_id,
            detail={"enrichments_added": len(enriched_event["enrichment"]["enrichments"])}
        )
        
        # Forward to SQS via EventBridge
        return {
            "statusCode": 200,
            "body": json.dumps(enriched_event)
        }
        
    except Exception as e:
        event_id = event.get("detail", {}).get("eventId", "unknown")
        log_event(
            action="EnrichEvent",
            status="FAILED",
            event_id=event_id,
            request_id=request_id,
            error=str(e)
        )
        raise

def enrich_geolocation(event_detail):
    """Add geolocation context to event."""
    return {
        "sourceIP": event_detail.get("sourceIP"),
        "country": event_detail.get("country", "Unknown"),
        "region": event_detail.get("region", "Unknown"),
        "riskIndicator": "UNUSUAL_GEOGRAPHY" if is_unusual_location(event_detail) else "NORMAL"
    }

def enrich_account(event_detail):
    """Add account context to event."""
    account_id = event_detail.get("accountId")
    return {
        "accountId": account_id,
        "accountName": f"Account-{account_id[-4:]}" if account_id else "Unknown",
        "accountType": "Production",  # In production, look this up
        "riskProfile": "High" if event_detail.get("eventType") == "IAMPolicyChange" else "Normal"
    }

def enrich_user(event_detail):
    """Add user context to event."""
    user = event_detail.get("user", "unknown")
    return {
        "userId": user,
        "userType": "Service" if "-" in user else "Human",
        "isRootAccount": user == "root",
        "mfaEnabled": event_detail.get("mfaUsed", False),
        "lastActivity": "Unknown"  # In production, look this up from CloudTrail
    }

def enrich_asset(event_detail):
    """Add asset context to event."""
    resource = event_detail.get("resource", "")
    return {
        "resourceType": extract_resource_type(resource),
        "resourceId": resource,
        "owner": "TeamA",  # In production, look this up from tags
        "classification": "Confidential",  # In production, look this up from tags
        "isProduction": "production" in resource.lower()
    }

def enrich_threat_indicators(event_detail):
    """Add threat intelligence indicators."""
    event_type = event_detail.get("eventType")
    base_weight = EVENT_TYPE_WEIGHTS.get(event_type, 0.5)
    
    return {
        "eventTypeWeight": base_weight,
        "failureIndicator": event_detail.get("result") == "FAIL" or event_detail.get("result") == "FAILED",
        "rateLimitIndicator": event_detail.get("rateLimitExceeded", False),
        "multipleAttemptsIndicator": event_detail.get("attemptCount", 1) > 1,
        "rootAccountIndicator": event_detail.get("user") == "root"
    }

def is_unusual_location(event_detail):
    """Check if location is unusual."""
    current_country = event_detail.get("country")
    previous_country = event_detail.get("previousLoginCountry")
    
    if not previous_country:
        return False
    
    return current_country != previous_country

def extract_resource_type(resource):
    """Extract resource type from ARN or resource string."""
    if "::" in resource:  # CloudFormation format
        return resource.split("::")[1]
    elif ":" in resource:  # ARN format
        parts = resource.split(":")
        if len(parts) >= 6:
            return parts[5].split("/")[0]
    return "Unknown"
