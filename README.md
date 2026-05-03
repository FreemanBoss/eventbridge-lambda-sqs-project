# Event-Driven Security Pipeline: Production-Grade Workshop

**AWS Cloud Security UserGroup West Africa**  
**Session Date:** May 2, 2026 | 60-Minute Workshop
**Topic:** Build an event-driven system using EventBridge + Lambda + SQS

---

## 📋 Overview

This project demonstrates a **production-grade, security-focused event-driven system** that ingests, enriches, scores, and processes security events in real-time using AWS EventBridge, Lambda, and SQS.

### What You'll Build

A complete event triage pipeline that:
- ✅ Routes suspicious activity events in real-time
- ✅ Enriches events with context (user, account, geo, asset metadata)
- ✅ Scores threat risk (0–100)
- ✅ Queues for reliable processing with guaranteed delivery
- ✅ Handles failures gracefully (retries, DLQ, circuit breaker)
- ✅ Provides full observability (X-Ray, CloudWatch, structured logs)
- ✅ Follows production best practices (least-privilege IAM, encryption, idempotency)

### Architecture Pattern

```
Events → EventBridge Rules → Lambda Enrichment/Scoring → SQS → Lambda Worker → Audit Trail
```

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with admin access (or sufficient permissions for EventBridge, Lambda, SQS, CloudWatch, X-Ray)
- AWS CLI v2 configured
- Python 3.11+
- Node.js 18+ (for AWS CDK)
- Docker (optional, for LocalStack testing)

### Installation

```bash
# Clone repo
git clone https://github.com/<owner>/<repo>.git
cd <repo>

# Install CDK dependencies
npm install -g aws-cdk

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r infrastructure/cdk/requirements.txt
pip install -r scripts/requirements.txt

# Install function dependencies
for func in functions/enricher functions/scorer functions/worker; do
  pip install -r $func/requirements.txt --target $func/package
done
```

### Deploy

```bash
cd infrastructure/cdk
cdk deploy --require-approval never
```

### Run Demo

```bash
# Send sample events to EventBridge
./scripts/send_events.sh

# Watch logs in real-time
./scripts/monitor.sh
```

### Cleanup

```bash
./scripts/destroy.sh
```

---

## 📁 Project Structure

```
.
├── infrastructure/
│   ├── cdk/
│   │   ├── app.py                 # Main CDK application
│   │   ├── eventbridge_stack.py   # EventBridge resources
│   │   ├── lambda_stack.py        # Lambda functions
│   │   ├── sqs_stack.py           # SQS queues
│   │   ├── iam_stack.py           # IAM roles & policies
│   │   ├── monitoring_stack.py    # CloudWatch & X-Ray
│   │   └── requirements.txt
│   └── outputs/                   # Deployed resource outputs
│
├── functions/
│   ├── enricher/
│   │   ├── lambda_function.py     # Enrichment logic
│   │   ├── requirements.txt
│   │   └── tests/
│   │
│   ├── scorer/
│   │   ├── lambda_function.py     # Risk scoring logic
│   │   ├── requirements.txt
│   │   └── tests/
│   │
│   ├── worker/
│   │   ├── lambda_function.py     # SQS consumer & processor
│   │   ├── requirements.txt
│   │   └── tests/
│   │
│   └── shared/
│       ├── logger.py              # Structured logging
│       ├── validator.py           # Event validation
│       ├── idempotency.py         # Idempotent processing
│       └── constants.py           # Constants & config
│
├── events/
│   ├── sample_events.json         # Test event collection
│   └── schema.json                # EventBridge schema
│
├── tests/
│   ├── unit/                      # Unit tests for each Lambda
│   ├── integration/               # End-to-end flow tests
│   └── chaos/                     # Failure scenario tests
│
├── scripts/
│   ├── deploy.sh                  # Deploy infrastructure
│   ├── send_events.sh             # Simulate events
│   ├── monitor.sh                 # Watch logs/metrics
│   └── destroy.sh                 # Cleanup
│
├── docs/
│   ├── ARCHITECTURE.md            # Design decisions
│   ├── DEPLOYMENT.md              # Step-by-step guide
│   ├── RUNBOOK.md                 # Troubleshooting
│   └── PRODUCTION_CHECKLIST.md    # Pre-production readiness
│
└── .gitignore
```

---

## 🔧 Key Features

### 🛡️ Security
- **Least-Privilege IAM**: Each component has minimal required permissions
- **Encryption**: KMS for SQS, TLS in-flight, no secrets in code
- **Audit Trail**: Every event logged with correlation ID
- **Schema Validation**: Events validated against contract before processing

### 🔄 Resilience
- **Retry Strategy**: Exponential backoff, max 2 attempts per rule
- **Dead-Letter Queues**: Failed events captured for investigation
- **Idempotent Processing**: Same event processed twice = same outcome
- **Circuit Breaker**: Stop retrying if target repeatedly fails

### 📊 Observability
- **CloudWatch Logs**: Structured JSON logging
- **X-Ray Tracing**: End-to-end request flow visualization
- **Metrics Dashboard**: Event volume, latency, error rates
- **Alarms**: Alert on anomalies (queue depth, errors, latency)

### 🚀 Production-Ready
- **Infrastructure as Code**: CDK for reproducible deployments
- **Automated Tests**: Unit, integration, and chaos scenarios
- **Comprehensive Docs**: Architecture, deployment, troubleshooting
- **Cost Monitoring**: Track spend per event type

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design overview, decisions, data flows |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Step-by-step deployment walkthrough |
| [RUNBOOK.md](docs/RUNBOOK.md) | Operational guide and troubleshooting |
| [PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md) | Pre-launch readiness checklist |

---

## 🧪 Running Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Chaos engineering tests
pytest tests/chaos -v

# All tests with coverage
pytest tests/ --cov=functions
```

---

## 🎯 Learning Outcomes

After this workshop, you'll understand:
1. ✅ How to design event-driven security pipelines
2. ✅ EventBridge routing, filtering, and schema validation
3. ✅ Lambda as a stateless event processor (best practices)
4. ✅ SQS for decoupling and guaranteed delivery
5. ✅ Production patterns: retry, DLQ, idempotency, circuit breaker
6. ✅ Security controls at each layer (IAM, encryption, audit)
7. ✅ Observability: logging, tracing, metrics, alarms
8. ✅ How to adapt this pattern for your own use cases

---

## 🤝 Extending the Project

Once the core works, you can add:
- **SNS Notifications**: Alert on critical events
- **Lambda Remediation**: Auto-respond to threats
- **DynamoDB**: Event history and analytics
- **S3**: Archive events for compliance
- **EventBridge Archive**: Replay events if needed
- **Multi-Region**: Cross-region failover

---

## 💡 Real-World Use Cases

This pattern applies to:
- **Threat Detection**: Ingest CloudTrail, detect suspicious API calls
- **Compliance Monitoring**: Track configuration changes, audit events
- **Incident Response**: Correlate events, trigger auto-remediation
- **Cost Optimization**: Monitor unusual resource creation
- **Access Management**: Track role assumption, permission changes

---

## 📞 Support

- **Questions?** See [RUNBOOK.md](docs/RUNBOOK.md)
- **Deployment issues?** See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Code issues?** Check tests/ directory for examples

---

**Built for AWS Cloud Security UserGroup West Africa**
