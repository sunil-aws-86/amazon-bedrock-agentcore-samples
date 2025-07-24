#!/bin/bash

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_NAME="sre_agent"
RUNTIME_NAME="${RUNTIME_NAME:-sre_agent}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"

# Get current caller identity and construct role ARN
CALLER_IDENTITY=$(aws sts get-caller-identity --output json)
CURRENT_ARN=$(echo $CALLER_IDENTITY | jq -r '.Arn')

# Extract role name from ARN and construct role ARN
# This handles both assumed-role and user scenarios
if [[ $CURRENT_ARN == *":assumed-role/"* ]]; then
    # Extract role name from assumed role ARN
    ROLE_NAME=$(echo $CURRENT_ARN | sed 's/.*:assumed-role\/\([^\/]*\).*/\1/')
    ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
else
    # Default role if not running with an assumed role
    ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/BedrockAgentCoreRole"
    echo "⚠️  Not running with an assumed role. Will use default role: $ROLE_ARN"
fi

# Allow override via environment variable
ROLE_ARN="${AGENT_ROLE_ARN:-$ROLE_ARN}"

echo "🔐 Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Create repository if it doesn't exist
echo "📦 Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" || \
    aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION"

# Set up QEMU for ARM64 emulation
echo "🔧 Setting up QEMU for ARM64 emulation..."
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Build the Docker image for ARM64 (Dockerfile is at root level)
echo "🏗️ Building Docker image for linux/arm64 (this may take longer due to emulation)..."
DOCKER_BUILDKIT=0 docker build -f "$PARENT_DIR/Dockerfile" -t "$ECR_REPO_NAME" "$PARENT_DIR"

# Tag the image
echo "🏷️ Tagging image..."
docker tag "$ECR_REPO_NAME":latest "$ECR_REPO_URI":latest

# Push the image to ECR
echo "⬆️ Pushing image to ECR..."
docker push "$ECR_REPO_URI":latest

echo "✅ Successfully built and pushed image to:"
echo "$ECR_REPO_URI:latest"

# Save the container URI to a file in the script directory
echo "💾 Saving container URI to .sre_agent_uri file..."
echo "$ECR_REPO_URI:latest" > "$SCRIPT_DIR/.sre_agent_uri"
echo "Container URI saved to $SCRIPT_DIR/.sre_agent_uri"

# Deploy the agent runtime
echo ""
echo "🚀 Deploying agent runtime..."
echo "Using role ARN: $ROLE_ARN"
echo "Using runtime name: $RUNTIME_NAME"
echo "Using region: $AWS_REGION"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ Error: .env file not found at $SCRIPT_DIR/.env"
    echo "Please create a .env file with ANTHROPIC_API_KEY and GATEWAY_ACCESS_TOKEN"
    echo "You can use .env.example as a template"
    exit 1
fi

echo ".env file found at $SCRIPT_DIR/.env"

# Deploy using the Python script
cd "$SCRIPT_DIR"

# Create a temporary file to capture output
TEMP_OUTPUT=$(mktemp)

# Run the Python script and capture both return code and output
if python deploy_agent_runtime.py \
    --container-uri "$ECR_REPO_URI:latest" \
    --role-arn "$ROLE_ARN" \
    --runtime-name "$RUNTIME_NAME" \
    --region "$AWS_REGION" \
    --force-recreate > "$TEMP_OUTPUT" 2>&1; then
    
    # Success - show output
    DEPLOY_OUTPUT=$(cat "$TEMP_OUTPUT")
    echo "$DEPLOY_OUTPUT"
else
    # Failure - show error output and exit
    echo "❌ Agent runtime deployment failed!"
    echo "Error output:"
    cat "$TEMP_OUTPUT"
    rm -f "$TEMP_OUTPUT"
    exit 1
fi

# Clean up temporary file
rm -f "$TEMP_OUTPUT"

echo ""
echo "🎉 Build and deployment complete!"