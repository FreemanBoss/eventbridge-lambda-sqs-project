"""
Sample security events for testing and demonstration.
Represents real-world suspicious activities across multiple event types.
"""

SAMPLE_EVENTS = [
    {
        "eventId": "evt-001-unauthorized-api",
        "eventType": "UnauthorizedAPICall",
        "timestamp": "2026-05-02T10:15:00Z",
        "sourceIP": "192.168.1.100",
        "user": "john.doe@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "action": "DeleteDBInstance",
        "resource": "arn:aws:rds:us-east-1:123456789012:db:production-db",
        "result": "FAIL",
        "errorCode": "UnauthorizedOperation"
    },
    {
        "eventId": "evt-002-console-login-success",
        "eventType": "ConsoleLogin",
        "timestamp": "2026-05-02T10:20:15Z",
        "sourceIP": "203.0.113.42",
        "user": "admin@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "mfaUsed": True,
        "loginStatus": "SUCCESS",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0)"
    },
    {
        "eventId": "evt-003-console-login-failed",
        "eventType": "ConsoleLogin",
        "timestamp": "2026-05-02T10:22:00Z",
        "sourceIP": "198.51.100.85",
        "user": "unknown.user@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "mfaUsed": False,
        "loginStatus": "FAILED",
        "failureReason": "InvalidUserPassword",
        "attemptCount": 3
    },
    {
        "eventId": "evt-004-iam-policy-change",
        "eventType": "IAMPolicyChange",
        "timestamp": "2026-05-02T10:25:30Z",
        "sourceIP": "10.0.0.50",
        "user": "devops-automation@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "action": "PutUserPolicy",
        "principalName": "ec2-instance-role",
        "policyName": "AdminFullAccess",
        "changeType": "CREATE"
    },
    {
        "eventId": "evt-005-s3-unauthorized-access",
        "eventType": "S3ObjectAccess",
        "timestamp": "2026-05-02T10:30:00Z",
        "sourceIP": "192.0.2.15",
        "user": "external-contractor@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "bucketName": "sensitive-data-bucket",
        "objectKey": "financial-reports/2026-Q1.xlsx",
        "action": "GetObject",
        "result": "DENIED",
        "reason": "AccessDenied"
    },
    {
        "eventId": "evt-006-network-anomaly",
        "eventType": "NetworkAnomalyDetected",
        "timestamp": "2026-05-02T10:35:15Z",
        "sourceIP": "203.0.113.100",
        "user": "unknown",
        "accountId": "123456789012",
        "region": "us-east-1",
        "anomalyType": "PortScan",
        "targetPorts": [22, 80, 443, 3389],
        "packetCount": 5000,
        "timeWindow": "5min"
    },
    {
        "eventId": "evt-007-config-drift",
        "eventType": "ConfigurationDrift",
        "timestamp": "2026-05-02T10:40:00Z",
        "sourceIP": "10.0.1.10",
        "user": "terraform-bot@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "resourceType": "AWS::EC2::SecurityGroup",
        "resourceId": "sg-0123456789abcdef0",
        "changeType": "MODIFIED",
        "details": "Inbound rule added allowing port 22 from 0.0.0.0/0"
    },
    {
        "eventId": "evt-008-role-assumption",
        "eventType": "RoleAssumption",
        "timestamp": "2026-05-02T10:45:30Z",
        "sourceIP": "192.168.50.100",
        "user": "service-account@example.com",
        "accountId": "123456789012",
        "sourceAccountId": "987654321098",
        "region": "us-east-1",
        "assumedRoleName": "CrossAccountAdminRole",
        "sessionDuration": 3600,
        "mfaUsed": False
    },
    {
        "eventId": "evt-009-access-key-created",
        "eventType": "AccessKeyCreated",
        "timestamp": "2026-05-02T10:50:00Z",
        "sourceIP": "203.0.113.200",
        "user": "developer@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "principalName": "developer",
        "accessKeyId": "ACCESS_KEY_ID_EXAMPLE",
        "mfaUsed": True
    },
    {
        "eventId": "evt-010-high-volume-api-calls",
        "eventType": "UnauthorizedAPICall",
        "timestamp": "2026-05-02T11:00:00Z",
        "sourceIP": "198.51.100.200",
        "user": "batch-process@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "errorCount": 500,
        "successCount": 0,
        "timeWindow": "1min",
        "rateLimitExceeded": True
    },
    {
        "eventId": "evt-011-suspicious-geo",
        "eventType": "ConsoleLogin",
        "timestamp": "2026-05-02T11:05:45Z",
        "sourceIP": "41.215.85.50",  # Nigeria IP
        "user": "jane.smith@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "country": "NG",
        "previousLoginCountry": "US",
        "timeSinceLastLogin": "12h",
        "mfaUsed": False,
        "loginStatus": "SUCCESS"
    },
    {
        "eventId": "evt-012-root-account-access",
        "eventType": "ConsoleLogin",
        "timestamp": "2026-05-02T11:10:00Z",
        "sourceIP": "192.0.2.200",
        "user": "root",
        "accountId": "123456789012",
        "region": "us-east-1",
        "mfaUsed": False,
        "loginStatus": "SUCCESS",
        "criticalFlag": True
    },
    {
        "eventId": "evt-013-lambda-code-injection",
        "eventType": "UnauthorizedAPICall",
        "timestamp": "2026-05-02T11:15:30Z",
        "sourceIP": "203.0.113.75",
        "user": "unknown-app@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "action": "UpdateFunctionCode",
        "functionName": "SecurityEventProcessor",
        "result": "FAILED",
        "errorCode": "AccessDenied"
    },
    {
        "eventId": "evt-014-large-data-export",
        "eventType": "S3ObjectAccess",
        "timestamp": "2026-05-02T11:20:00Z",
        "sourceIP": "192.168.100.50",
        "user": "analyst@example.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "bucketName": "customer-data-bucket",
        "action": "GetObject",
        "objectSize": 10737418240,  # 10 GB
        "result": "SUCCESS",
        "transferTime": 600  # seconds
    },
    {
        "eventId": "evt-015-database-credential-exposure",
        "eventType": "UnauthorizedAPICall",
        "timestamp": "2026-05-02T11:25:15Z",
        "sourceIP": "203.0.113.150",
        "user": "contractor@external.com",
        "accountId": "123456789012",
        "region": "us-east-1",
        "action": "DescribeDBInstances",
        "resource": "arn:aws:rds:us-east-1:123456789012:db:*",
        "result": "SUCCESS",
        "credentialSource": "PublicGitHubRepo"
    }
]

def get_sample_event(event_index: int = 0) -> dict:
    """Get a sample event for testing."""
    return SAMPLE_EVENTS[event_index % len(SAMPLE_EVENTS)]

def get_all_sample_events() -> list:
    """Get all sample events."""
    return SAMPLE_EVENTS

if __name__ == "__main__":
    import json
    print(json.dumps({"events": SAMPLE_EVENTS}, indent=2))
