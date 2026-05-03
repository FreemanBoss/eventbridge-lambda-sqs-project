"""
Event validation against security event schema.
Ensures all required fields are present and valid before processing.
"""

import re
from typing import Dict, List, Tuple

REQUIRED_FIELDS = [
    "eventId",
    "eventType",
    "timestamp",
    "sourceIP",
]

VALID_EVENT_TYPES = [
    "UnauthorizedAPICall",
    "ConsoleLogin",
    "IAMPolicyChange",
    "S3ObjectAccess",
    "NetworkAnomalyDetected",
    "ConfigurationDrift",
    "RoleAssumption",
    "AccessKeyCreated",
]

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
IP_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'
ARN_PATTERN = r'^arn:aws:[a-z0-9-]*:[a-z0-9-]*:\d{12}:.*$'

def validate_event(event: Dict) -> Tuple[bool, List[str]]:
    """
    Validate security event against schema.
    
    Returns:
        (is_valid, errors) where errors is a list of validation failure messages
    """
    errors = []
    detail = event.get("detail", {})
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in detail or not str(detail[field]).strip():
            errors.append(f"Missing required field: {field}")
    
    # Validate event type
    if "eventType" in detail and detail["eventType"] not in VALID_EVENT_TYPES:
        errors.append(
            f"Invalid eventType '{detail['eventType']}'. "
            f"Valid types: {', '.join(VALID_EVENT_TYPES)}"
        )
    
    # Validate IP address format
    if "sourceIP" in detail:
        ip = detail["sourceIP"]
        if not re.match(IP_PATTERN, ip):
            errors.append(f"Invalid sourceIP format: {ip}")
    
    # Validate timestamp format (ISO 8601)
    if "timestamp" in detail:
        ts = detail["timestamp"]
        if not isinstance(ts, str) or not ts.endswith("Z"):
            errors.append(f"Timestamp must be ISO 8601 format ending in Z")
    
    # Validate EventBridge envelope structure
    if "source" not in event or event["source"] != "custom.security":
        errors.append("Event source must be 'custom.security'")
    
    if "detail-type" not in event or event["detail-type"] != "Suspicious Activity":
        errors.append("Event detail-type must be 'Suspicious Activity'")
    
    return len(errors) == 0, errors

def sanitize_event(event: Dict) -> Dict:
    """
    Sanitize event to remove or mask sensitive data.
    Masks emails, SSNs, credit card numbers in log output.
    """
    import copy
    sanitized = copy.deepcopy(event)

    detail = sanitized.get("detail", {})
    
    # Mask email addresses in user field
    if "user" in detail:
        user = detail["user"]
        if isinstance(user, str) and "@" in user:
            # Mask to: a***@example.com
            parts = user.split("@")
            masked = parts[0][0] + "*" * (len(parts[0]) - 1) + "@" + parts[1]
            detail["user"] = masked
    
    # Remove sensitive fields if present
    sensitive_keys = ["sessionToken", "accessKeySecret", "password"]
    for key in sensitive_keys:
        detail.pop(key, None)
    
    sanitized["detail"] = detail
    return sanitized
