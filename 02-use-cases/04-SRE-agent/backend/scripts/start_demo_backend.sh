#!/bin/bash
# Start all demo backend servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

echo "🚀 Starting SRE Agent Demo Backend..."

# Check if we're in the right directory
if [ ! -d "$BACKEND_DIR/data" ]; then
    echo "❌ Backend data directory not found. Please run from backend/ directory"
    exit 1
fi

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Start FastAPI servers using the proper server implementations
echo "📊 Starting FastAPI servers..."

# Change to servers directory
cd "$BACKEND_DIR/servers"

# K8s API Server (Port 8011)
echo "🏗️  Starting Kubernetes API server on port 8011..."
nohup python3 k8s_server.py > "$PROJECT_ROOT/logs/k8s_server.log" 2>&1 &

# Logs API Server (Port 8012)
echo "📋 Starting Logs API server on port 8012..."
nohup python3 logs_server.py > "$PROJECT_ROOT/logs/logs_server.log" 2>&1 &

# Metrics API Server (Port 8013)
echo "📈 Starting Metrics API server on port 8013..."
nohup python3 metrics_server.py > "$PROJECT_ROOT/logs/metrics_server.log" 2>&1 &

# Runbooks API Server (Port 8014)
echo "📚 Starting Runbooks API server on port 8014..."
nohup python3 runbooks_server.py > "$PROJECT_ROOT/logs/runbooks_server.log" 2>&1 &

# Wait a moment for servers to start
sleep 2

echo "✅ Demo backend started successfully!"
echo "📊 K8s API: http://localhost:8011"
echo "📋 Logs API: http://localhost:8012" 
echo "📈 Metrics API: http://localhost:8013"
echo "📚 Runbooks API: http://localhost:8014"
echo ""
echo "📝 Logs are being written to $PROJECT_ROOT/logs/"
echo "🛑 Use './scripts/stop_demo_backend.sh' to stop all servers"