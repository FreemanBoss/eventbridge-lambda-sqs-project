#!/bin/bash
set -e

PROJECT_NAME="SecurityEventPipeline"
REGION="${AWS_REGION:-us-east-1}"

echo "🚀 Starting CDK deployment of $PROJECT_NAME..."
echo "📍 Region: $REGION"

# Install dependencies
echo "📦 Installing dependencies..."
npm install -g aws-cdk
cd infrastructure/cdk
pip install -r requirements.txt

# Build the project
echo "🔨 Building CDK project..."
cdk synth

# Deploy all stacks
echo "⚙️  Deploying infrastructure..."
cdk deploy --all --require-approval never --profile "$AWS_PROFILE"

# Output deployment info
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=SecurityEventPipeline"
echo ""
echo "Next steps:"
echo "  1. Send test events:    ./scripts/send_events.sh"
echo "  2. Monitor:             ./scripts/monitor.sh"
echo "  3. Cleanup:             ./scripts/destroy.sh"
