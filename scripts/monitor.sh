#!/bin/bash

REGION="${AWS_REGION:-us-east-1}"

echo "🔍 Monitoring Security Event Pipeline..."
echo "📍 Region: $REGION"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to display Lambda logs
show_lambda_logs() {
    local func_name=$1
    local log_group="/aws/lambda/$func_name"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 $func_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    aws logs tail "$log_group" \
        --region "$REGION" \
        --follow \
        --format short \
        --max-items 10 2>/dev/null || echo "  ⏳ Waiting for logs..."
    
    echo ""
}

# Function to display SQS metrics
show_sqs_metrics() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 SQS Queue Metrics"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    QUEUE_URL=$(aws sqs get-queue-url \
        --queue-name "SecurityEventQueue" \
        --region "$REGION" \
        --query 'QueueUrl' \
        --output text 2>/dev/null)
    
    if [ -n "$QUEUE_URL" ]; then
        ATTRS=$(aws sqs get-queue-attributes \
            --queue-url "$QUEUE_URL" \
            --attribute-names "ApproximateNumberOfMessages" "ApproximateNumberOfMessagesNotVisible" \
            --region "$REGION" \
            --query 'Attributes' \
            --output json 2>/dev/null)
        
        echo "Queue Attributes: $ATTRS"
    else
        echo "  ⏳ Queue not found yet"
    fi
    
    echo ""
}

# Continuous monitoring
while true; do
    clear
    echo "🔴 LIVE MONITORING - $(date)"
    echo ""
    
    show_lambda_logs "SecurityEnricherFunction"
    show_lambda_logs "SecurityScorerFunction"
    show_sqs_metrics
    
    echo "🔄 Refreshing in 10 seconds... (Press Ctrl+C to exit)"
    sleep 10
done
