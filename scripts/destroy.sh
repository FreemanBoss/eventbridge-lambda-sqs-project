#!/bin/bash
set -e

PROJECT_NAME="SecurityEventPipeline"
REGION="${AWS_REGION:-us-east-1}"

echo "🗑️  Destroying CDK resources for $PROJECT_NAME..."
echo "⚠️  This will delete all AWS resources created by this project"
echo ""

read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "🔄 Deleting CloudFormation stacks..."
STACKS=$(aws cloudformation list-stacks --region "$REGION" --profile "$AWS_PROFILE" --query "StackSummaries[?StackStatus!='DELETE_COMPLETE'].StackName" --output text)

for stack in $STACKS; do
    echo "Deleting $stack..."
    aws cloudformation delete-stack --stack-name "$stack" --region "$REGION" --profile "$AWS_PROFILE"
done

for stack in $STACKS; do
    echo "Waiting for $stack..."
    aws cloudformation wait stack-delete-complete --stack-name "$stack" --region "$REGION" --profile "$AWS_PROFILE"
done

echo ""
echo "✅ Resources destroyed!"
