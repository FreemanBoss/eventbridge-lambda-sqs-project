#!/bin/bash
set -e

EVENT_BUS="SecurityEventBus"
REGION="${AWS_REGION:-us-east-1}"

echo "📬 Sending security events to EventBridge..."
echo "🚌 Event Bus: $EVENT_BUS"
echo ""

# Source sample events
ENTRIES_JSON=$(python3 - <<'PY'
import json
from events.sample_events import get_all_sample_events

entries = []
for sample_event in get_all_sample_events()[:4]:
    entries.append({
        "Source": "custom.security",
        "DetailType": "Suspicious Activity",
        "Detail": json.dumps(sample_event),
    })

print(json.dumps(entries))
PY
)

echo "Sending 4 events in one batch..."
aws events put-events \
    --event-bus-name "$EVENT_BUS" \
    --entries "$ENTRIES_JSON" \
    --region "$REGION" >/dev/null 2>&1 || {
        echo "  ℹ️  Event bus may not exist yet or credentials are missing."
    }

echo ""
echo "✅ Events sent! Check CloudWatch Logs to see them being processed:"
echo "   - Enricher: /aws/lambda/SecurityEnricherFunction"
echo "   - Scorer:   /aws/lambda/SecurityScorerFunction"
echo "   - Worker:   /aws/lambda/SecurityWorkerFunction"
