# Production-Grade Event-Driven Security Pipeline
## AWS Cloud Security UserGroup Workshop — May 2, 2026

---

## VISION: What Makes This "Industrial Standard"

This project demonstrates a **Security Event Triage & Response Pipeline** that handles:
1. Real-time threat detection event ingestion
2. Intelligent event enrichment and risk scoring
3. Resilient, decoupled processing with guaranteed delivery
4. Comprehensive observability and compliance auditing
5. Production hardening: idempotency, retry strategies, circuit breakers
6. Security-first architecture with least-privilege IAM and encryption

**Why this matters:**
- Most teams build simple event flows and then hit production failures
- This project shows the REAL patterns: retry policies, DLQs, correlation tracking, schema validation, chaos handling
- Security teams need event-driven systems for threat detection, compliance monitoring, and incident response
- Attendees leave with copy-paste-ready, battle-tested code

---

## ARCHITECTURE: The Full Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SECURITY EVENT SOURCES (Simulated)                                          │
│  - CloudTrail API calls (suspicious)                                         │
│  - IAM policy changes                                                        │
│  - Unauthorized access attempts                                              │
│  - Configuration drifts                                                      │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │ (JSON events via boto3 or custom webhook)
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EVENTBRIDGE CUSTOM EVENT BUS                                               │
│  - Event routing rules (schema-based)                                        │
│  - Event filtering (reduce noise)                                            │
│  - Event transformation (optional)                                           │
│  - Dead-letter queue for rule failures                                       │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼
    ┌─────────────────┐              ┌──────────────────┐
    │ CRITICAL EVENTS │              │ ROUTINE EVENTS   │
    │ (Risk > 75)     │              │ (Risk < 75)      │
    └────────┬────────┘              └────────┬─────────┘
             │                                │
             ▼                                ▼
    ┌─────────────────────────┐      ┌────────────────────┐
    │ LAMBDA: ENRICHER        │      │ LAMBDA: SCORER     │
    │ - Add context (user,    │      │ - Compute risk     │
    │   account, region)      │      │ - Add metadata     │
    │ - Cross-ref lookups     │      │ - Format output    │
    │ - X-Ray trace tags      │      │ - X-Ray tracing    │
    └──────────┬──────────────┘      └────────┬───────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
                    ┌──────────────────────┐
                    │ SQS QUEUE            │
                    │ - Guaranteed delivery│
                    │ - Visibility timeout │
                    │ - DLQ for failures   │
                    │ - Encryption enabled │
                    └──────────┬───────────┘
                               │
   ┌───────────────────────────┼───────────────────────────┐
   │                           │                           │
   ▼                           ▼                           ▼
┌─────────────────┐  ┌──────────────────┐   ┌──────────────────┐
│ LAMBDA: WORKER  │  │ LAMBDA: NOTIFIER │   │ LAMBDA: ARCHIVER │
│ - Idempotent    │  │ - Send alerts    │   │ - Store to S3    │
│   processing    │  │ - PagerDuty      │   │ - Compliance     │
│ - Batch items   │  │ - Slack/Email    │   │   records        │
│ - Error retry   │  │ - Track delivery │   │ - Query indexed  │
└────────┬────────┘  └─────────┬────────┘   └────────┬─────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ OBSERVABILITY LAYER  │
                    │ - CloudWatch logs    │
                    │ - X-Ray traces       │
                    │ - Metrics dashboards │
                    │ - Alarms             │
                    │ - Cost monitoring    │
                    └──────────────────────┘
```

---

## CORE FEATURES: What Makes This Production-Grade

### 1. EVENT VALIDATION & SCHEMA ENFORCEMENT
- **EventBridge Event Schema Registry** with versioning
- Input validation before processing (block malformed events early)
- Reject events that don't match security event contract

### 2. RESILIENCE & RELIABILITY
- **Retry Policies:** Exponential backoff (1s → 2s → 4s → 8s → fail)
- **Dead-Letter Queues (DLQs):** Capture failed events for investigation
- **Idempotent Processing:** Same event processed twice = same result
- **Circuit Breaker Pattern:** Stop retrying if target is down too long
- **Batch Processing:** SQS batch window optimization (10 events per Lambda invocation)

### 3. SECURITY & COMPLIANCE
- **Least-Privilege IAM:** Each Lambda, EventBridge rule, and SQS has minimal permissions
- **Encryption:** KMS for SQS, in-flight TLS, encryption at rest
- **Audit Trail:** Every event logged with correlation ID, timestamp, actor
- **Schema Versioning:** Track event structure changes over time
- **Sensitive Data Masking:** PII redaction in logs (email, SSN patterns)

### 4. OBSERVABILITY & DEBUGGING
- **Structured Logging:** JSON logs with requestId, eventId, userId, action, result
- **X-Ray Tracing:** End-to-end request flow visualization
- **CloudWatch Metrics:** Event volume, processing latency, error rate per service
- **Dashboards:** Real-time view of pipeline health
- **Alarms:** Alert on error rates, queue depth, DLQ messages

### 5. SCALABILITY & COST
- **EventBridge routing:** Filter early to reduce Lambda invocations
- **SQS batching:** Group events for efficient processing
- **Reserved Concurrency:** Protect critical functions from throttling
- **Cost Tags:** Track spend per event type
- **Regional failover ready:** Code supports multi-region deployment

### 6. OPERATIONAL EXCELLENCE
- **Infrastructure as Code (CDK):** Reproducible, version-controlled infrastructure
- **Runbooks:** Troubleshooting guides for common failures
- **Tests:** Unit tests, integration tests, chaos engineering scenarios
- **Documentation:** Architecture decisions, deployment instructions, runbooks

---

## STEP-BY-STEP BUILD PLAN

### **PHASE 1: Foundation Setup **
**Deliverable:** Working local environment with AWS CLI, CDK, sample events
1. Create repo structure:
   ```
   eventbridge-lambda-sqs-security-pipeline/
   ├── README.md
   ├── infrastructure/
   │   ├── cdk/
   │   │   ├── app.py (main CDK app)
   │   │   ├── eventbridge_stack.py
   │   │   ├── lambda_stack.py
   │   │   ├── sqs_stack.py
   │   │   └── iam_stack.py
   │   └── outputs/ (deployed resource IDs)
   ├── functions/
   │   ├── enricher/
   │   │   ├── lambda_function.py
   │   │   ├── requirements.txt
   │   │   └── tests/
   │   ├── scorer/
   │   │   ├── lambda_function.py
   │   │   ├── requirements.txt
   │   │   └── tests/
   │   ├── worker/
   │   │   ├── lambda_function.py
   │   │   ├── requirements.txt
   │   │   └── tests/
   │   └── shared/
   │       ├── logger.py (structured logging)
   │       ├── validator.py (event schema validation)
   │       ├── idempotency.py (idempotent processing cache)
   │       └── constants.py
   ├── events/
   │   ├── sample_events.json (15+ test cases)
   │   └── schema.json (EventBridge schema)
   ├── tests/
   │   ├── unit/ (test each Lambda)
   │   ├── integration/ (test Lambda + SQS)
   │   └── chaos/ (simulate failures)
   ├── scripts/
   │   ├── deploy.sh (CDK deploy)
   │   ├── send_events.sh (simulate events)
   │   ├── monitor.sh (watch logs/metrics)
   │   └── destroy.sh (cleanup)
   ├── docs/
   │   ├── ARCHITECTURE.md
   │   ├── DEPLOYMENT.md
   │   ├── RUNBOOK.md
   │   └── TROUBLESHOOTING.md
   └── .github/workflows/
       ├── tests.yml (run on PR)
       └── deploy.yml (run on merge)
   ```

2. Set up AWS account and local credentials
3. Install tools: AWS CDK v2, Python 3.11, LocalStack (for local testing)
4. Create sample event file with 15+ realistic security event scenarios
5. Define EventBridge event schema

### **PHASE 2: Core Infrastructure**
**Deliverable:** EventBridge, SQS, Lambda roles deployed and tested
1. Build CDK stack:
   - EventBridge custom event bus
   - Routing rules (critical vs routine)
   - Dead-letter event bus
2. Create SQS queues:
   - Main processing queue
   - Dead-letter queue
   - DLQ for DLQ (capture unrecoverable events)
3. Define IAM roles with least-privilege policies:
   - EventBridge can invoke Lambda and send to SQS
   - Lambda can read SQS, write CloudWatch logs, put X-Ray traces
   - SQS encrypted with KMS key
4. Deploy and verify connectivity

### **PHASE 3: Lambda Functions**
**Deliverable:** Three Lambda functions working end-to-end
1. **Enricher Lambda:**
   - Receive event from EventBridge
   - Add user context (lookup user account details)
   - Add geographic context (IP → country/region)
   - Add asset context (EC2 instance details, IAM role)
   - Return enriched event to SQS
   - X-Ray tracing on all lookups
   - Structured JSON logging
   - Error handling with exponential backoff retry
   - Test: simulate enrichment latency and failures

2. **Scorer Lambda:**
   - Receive event from EventBridge (parallel path)
   - Compute risk score (0–100): threat_level × event_type_weight × recency
   - Assign severity: LOW, MEDIUM, HIGH, CRITICAL
   - Add detection timestamp and detector ID
   - Send to SQS
   - X-Ray tracing
   - Test: validate scoring logic with 10+ test cases

3. **Worker Lambda (SQS consumer):**
   - Batch process up to 10 SQS messages
   - Idempotent processing: check if eventId already processed (cache or DynamoDB)
   - Parse enriched + scored event
   - Simulate downstream processing: log to archive store, trigger notification
   - Delete from SQS on success
   - On failure: push to DLQ, trigger alarm
   - Test: force failures, verify DLQ routing

### **PHASE 4: Observability & Resilience**
**Deliverable:** Full monitoring, logging, tracing, and failure handling
1. **CloudWatch Dashboards:**
   - Event ingestion rate (events/min)
   - Processing latency
   - Error rate per Lambda
   - Queue depth (SQS ApproximateNumberOfMessages)
   - DLQ message count
   - Cost per event

2. **X-Ray Tracing:**
   - Instrument all Lambda functions
   - Trace EventBridge → Lambda → SQS → Worker latency
   - Capture service nodes and errors
   - Visualize in X-Ray service map

3. **Alarms:**
   - Alert if SQS queue depth > 100
   - Alert if DLQ message count > 0
   - Alert if Lambda error rate > 1%
   - Alert if processing latency p99 > 5s

4. **Chaos Engineering Tests:**
   - Simulate Lambda timeout
   - Simulate SQS unavailable
   - Simulate malformed events
   - Simulate DynamoDB throttling (idempotency store)
   - Verify circuit breaker activates

### **PHASE 5: Documentation & Testing**
**Deliverable:** Comprehensive docs, tests, and demo script ready
1. **Automated Tests (pytest):**
   - Unit tests: scoring logic, validation logic
   - Integration tests: EventBridge → Lambda → SQS flow
   - Mock AWS services (moto)

2. **Documentation:**
   - Architecture decision record (ADR): why these choices
   - Deployment guide: step-by-step to deploy yourself
   - Runbook: how to diagnose and fix common issues
   - Code comments on tricky parts
---

## PRODUCTION FEATURES IN DETAIL

### **Event Schema Validation**
```json
{
  "source": "custom.security",
  "detail-type": "Suspicious Activity",
  "detail": {
    "eventId": "evt-uuid",
    "eventType": "UnauthorizedAPICall",
    "user": "arn:aws:iam::123456789012:user/alice",
    "action": "s3:GetObject",
    "resource": "arn:aws:s3:::bucket/sensitive-data",
    "sourceIP": "203.0.113.45",
    "timestamp": "2026-05-02T14:23:15Z",
    "reason": "API call from unusual IP"
  }
}
```

### **Idempotent Processing**
- Store `(eventId, processingTimestamp)` in DynamoDB TTL cache
- On Worker Lambda: check if eventId exists in cache
- If yes: return success without re-processing
- If no: process and insert into cache
- TTL: 24 hours (deduplicate within same day)

### **Retry Strategy**
- EventBridge rule retry policy:
  - Max attempts: 2 (default EventBridge limit)
  - Dead-letter: send to DLQ after exhausted retries
- SQS retry (via Lambda):
  - Max receives: 3
  - Visibility timeout: 300s (5 minutes)
  - If Lambda fails: message stays in queue for retry
  - After 3 failures: move to DLQ

### **Least-Privilege IAM Example**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EventBridgeInvokeLambda",
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:ScorerFunction",
      "Condition": {
        "StringEquals": {
          "aws:source": "events.amazonaws.com"
        }
      }
    },
    {
      "Sid": "LambdaWriteToSQS",
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:*:*:SecurityEventQueue",
      "Condition": {
        "StringLike": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

### **Structured Logging**
```python
import json
import uuid
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

def handler(event, context):
    request_id = str(uuid.uuid4())
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "requestId": request_id,
        "function": context.function_name,
        "eventId": event.get("detail", {}).get("eventId"),
        "action": "ProcessEvent",
        "status": "STARTED",
        "detail": event
    }
    logger.info(json.dumps(log_entry))
    
    try:
        result = process(event)
        log_entry["status"] = "SUCCESS"
        logger.info(json.dumps(log_entry))
        return result
    except Exception as e:
        log_entry["status"] = "FAILED"
        log_entry["error"] = str(e)
        logger.error(json.dumps(log_entry))
        raise
```

---

## SUCCESS CRITERIA FOR PRODUCTION-GRADE

✅ **Resilience**: System survives Lambda timeout, SQS unavailable, malformed event  
✅ **Security**: Least-privilege IAM, encryption, audit trail, no secrets in code  
✅ **Observability**: X-Ray traces show every hop, metrics show health, logs are searchable  
✅ **Scalability**: Can handle 1000 events/min without error, batch processing  
✅ **Reliability**: Idempotent processing, no duplicate notifications, DLQ captures failures  
✅ **Documentation**: Code is clear, tests pass, runbook helps fix issues  
✅ **Real-World Patterns**: Uses patterns teams actually need: retry, DLQ, circuit breaker, tracing
