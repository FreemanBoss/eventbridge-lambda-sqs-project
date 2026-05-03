"""
Structured JSON logging for the security event pipeline.
Each log entry includes: timestamp, requestId, function, eventId, action, status, error.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove default handler and add JSON formatter
if logger.handlers:
    logger.handlers = []

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for CloudWatch parsing and X-Ray correlation."""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "function": record.name,
            "message": record.getMessage(),
        }
        
        # Include extra fields if provided
        if hasattr(record, "requestId"):
            log_obj["requestId"] = record.requestId
        if hasattr(record, "eventId"):
            log_obj["eventId"] = record.eventId
        if hasattr(record, "action"):
            log_obj["action"] = record.action
        if hasattr(record, "status"):
            log_obj["status"] = record.status
        if hasattr(record, "detail"):
            log_obj["detail"] = record.detail
        
        # Include exception if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)

# Attach JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

def log_event(
    action: str,
    status: str,
    event_id: Optional[str] = None,
    request_id: Optional[str] = None,
    detail: Optional[dict] = None,
    error: Optional[str] = None
):
    """
    Log a structured event.
    
    Args:
        action: What is being done (e.g., "ProcessEvent", "EnrichEvent")
        status: SUCCESS, FAILED, STARTED, IN_PROGRESS
        event_id: Security event ID
        request_id: Lambda request ID
        detail: Additional context dict
        error: Error message if failed
    """
    log_entry = {
        "action": action,
        "status": status,
        "eventId": event_id,
        "requestId": request_id,
        "detail": detail or {},
        "error": error
    }
    
    if status == "FAILED":
        logger.error(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

def get_request_id():
    """Generate a correlation ID for this request."""
    return str(uuid.uuid4())
