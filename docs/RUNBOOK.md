# Security Event Pipeline - Troubleshooting Guide

## Common Issues

### EventBridge Event Bus Not Found
**Error:** `An error occurred (ResourceNotFoundException) when calling the PutEvents operation`

**Solution:**
```bash
# Deploy infrastructure first
./scripts/deploy.sh

# Verify event bus exists
aws events list-event-buses --region us-east-1
```

### Lambda Function Not Triggered
**Check:**
1. Event bus routing rules are active
2. Lambda has execute permission from EventBridge
3. Check CloudWatch Logs for execution

```bash
# View Lambda logs
aws logs tail /aws/lambda/SecurityEnricherFunction --follow
```

### SQS Queue Empty
**Check:**
1. Worker Lambda successfully processed messages
2. DLQ for failed messages
3. Check DLQ for error details

```bash
# Check DLQ messages
aws sqs receive-message \
  --queue-url $(aws sqs get-queue-url --queue-name SecurityEventQueue-DLQ --query 'QueueUrl' --output text) \
  --max-number-of-messages 10
```

### Permission Denied Errors

**Solution:** Verify IAM roles and policies
```bash
# Check IAM role for Lambda
aws iam get-role --role-name SecurityEventPipelineIAMStackEnricherRole* --query 'Role.Arn'

# List inline policies
aws iam list-role-policies --role-name SecurityEventPipelineIAMStackEnricherRole*
```

## Debugging Steps

### 1. Enable X-Ray Tracing
Already enabled in CDK configuration. View traces:
```bash
# List recent traces
aws xray get-trace-summaries --start-time $(date -d '5 minutes ago' +%s)
```

### 2. Check Event Schema
```bash
# Verify event schema validation
aws events describe-event-bus --name SecurityEventBus
```

### 3. Monitor Performance
```bash
# CloudWatch metrics for Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=SecurityEnricherFunction \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S.000Z) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S.000Z) \
  --period 300 \
  --statistics Average
```

## Reset to Known Good State

```bash
# Destroy all resources
./scripts/destroy.sh

# Clear local state
rm -rf infrastructure/cdk/cdk.out
rm -rf infrastructure/cdk/.cdk.staging

# Redeploy
./scripts/deploy.sh
```

## Support

- Check logs: `./scripts/monitor.sh`
- Review code: `functions/*/lambda_function.py`
- Test locally: `pytest tests/unit -v`
