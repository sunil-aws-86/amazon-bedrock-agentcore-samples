#!/bin/bash

# Enhanced Bedrock Agent DynamoDB Integration - Installation Script
echo "🚀 Installing Enhanced Bedrock Agent DynamoDB Integration requirements..."

# Install beta wheel files first (required for Bedrock Agent Core Gateway)
echo "📦 Installing beta boto3/botocore wheels..."
pip install wheelhouse/botocore-1.39.3-py3-none-any.whl
pip install wheelhouse/boto3-1.39.3-py3-none-any.whl
pip install wheelhouse/awscli-1.41.3-py3-none-any.whl

# Install standard packages
echo "📦 Installing standard packages..."
pip install jupyter notebook requests urllib3

echo "✅ Installation complete!"
echo "🎯 Run 'jupyter notebook' to start the notebook environment"