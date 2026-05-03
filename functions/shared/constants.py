"""
Constants used throughout the event-driven pipeline.
"""

# Risk scoring thresholds
RISK_THRESHOLD_CRITICAL = 85
RISK_THRESHOLD_HIGH = 65
RISK_THRESHOLD_MEDIUM = 40
RISK_THRESHOLD_LOW = 0

# Risk levels
RISK_LEVEL_CRITICAL = "CRITICAL"
RISK_LEVEL_HIGH = "HIGH"
RISK_LEVEL_MEDIUM = "MEDIUM"
RISK_LEVEL_LOW = "LOW"

# Event types and their base risk weights
EVENT_TYPE_WEIGHTS = {
    "UnauthorizedAPICall": 0.8,      # High risk
    "ConsoleLogin": 0.4,             # Medium risk
    "IAMPolicyChange": 0.9,          # Very high risk
    "S3ObjectAccess": 0.3,           # Low risk
    "NetworkAnomalyDetected": 0.7,   # High risk
    "ConfigurationDrift": 0.6,       # Medium-high risk
    "RoleAssumption": 0.5,           # Medium risk
    "AccessKeyCreated": 0.8,         # High risk
}

# SQS queue names
QUEUE_NAME_SECURITY_EVENTS = "SecurityEventQueue"
QUEUE_NAME_SECURITY_EVENTS_DLQ = "SecurityEventQueue-DLQ"

# Lambda function names
FUNCTION_NAME_ENRICHER = "SecurityEnricher"
FUNCTION_NAME_SCORER = "SecurityScorer"
FUNCTION_NAME_WORKER = "SecurityWorker"

# EventBridge
EVENT_BUS_NAME = "SecurityEventBus"
EVENT_BUS_RULE_CRITICAL = "SecurityEventCritical"
EVENT_BUS_RULE_ROUTINE = "SecurityEventRoutine"

# Retry configuration
MAX_RETRY_ATTEMPTS = 2
RETRY_BACKOFF_BASE = 1000  # milliseconds
RETRY_BACKOFF_MAX = 60000  # milliseconds (60 seconds)

# SQS configuration
SQS_MESSAGE_VISIBILITY_TIMEOUT = 300  # 5 minutes
SQS_MESSAGE_RETENTION_PERIOD = 1209600  # 14 days

# Idempotency TTL
IDEMPOTENCY_TTL_HOURS = 24

# Logging
LOG_FORMAT_JSON = "json"
LOG_LEVEL_DEFAULT = "INFO"
