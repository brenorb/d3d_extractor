#!/bin/bash

echo "🐳 Docker Container Test Script"
echo "================================"

# Start overall timing
SCRIPT_START=$(date +%s)

# Function to format time in seconds to human readable format
format_time() {
    local seconds=$1
    if [ $seconds -ge 60 ]; then
        local minutes=$((seconds / 60))
        local remaining_seconds=$((seconds % 60))
        if [ $remaining_seconds -eq 0 ]; then
            echo "${minutes}m"
        else
            echo "${minutes}m ${remaining_seconds}s"
        fi
    else
        echo "${seconds}s"
    fi
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo ""
    echo "To install Docker Desktop on macOS:"
    echo "1. Visit: https://www.docker.com/products/docker-desktop/"
    echo "2. Download Docker Desktop for Mac"
    echo "3. Install and start Docker Desktop"
    echo "4. Run this script again"
    echo ""
    echo "Alternative: Install via Homebrew:"
    echo "   brew install --cask docker"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is available"

# Load environment variables from .env file
echo "📋 Loading environment variables from .env file..."
set -a  # automatically export all variables
source .env 2>/dev/null || echo "⚠️  Could not load .env file"
set +a  # stop automatically exporting
echo "✅ Environment variables loaded"

# Build the image
echo ""
echo "🔨 Building Docker image..."
BUILD_START=$(date +%s)
if docker build -t diabetes3d-api .; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    echo "✅ Docker image built successfully ($(format_time $BUILD_TIME))"
else
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    echo "❌ Docker build failed ($(format_time $BUILD_TIME))"
    exit 1
fi

# Test the container
echo ""
echo "🚀 Starting container..."
CONTAINER_ID=$(docker run -d -p 8001:8000 \
    -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
    -e MISTRAL_API_KEY="${MISTRAL_API_KEY}" \
    diabetes3d-api)

if [ $? -eq 0 ]; then
    echo "✅ Container started with ID: $CONTAINER_ID"
else
    echo "❌ Failed to start container"
    exit 1
fi

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 20

# Test health endpoint
echo ""
echo "🔍 Testing health endpoint..."
HEALTH_START=$(date +%s)
if curl -f http://localhost:8001/health; then
    HEALTH_END=$(date +%s)
    HEALTH_TIME=$((HEALTH_END - HEALTH_START))
    echo ""
    echo "✅ Health check passed ($(format_time $HEALTH_TIME))"
else
    HEALTH_END=$(date +%s)
    HEALTH_TIME=$((HEALTH_END - HEALTH_START))
    echo ""
    echo "❌ Health check failed ($(format_time $HEALTH_TIME))"
fi

# Test file upload endpoint
echo ""
echo "📄 Testing file upload with data/test_file.pdf..."
UPLOAD_START=$(date +%s)
if curl -f -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "file=@data/test_file.pdf" \
    http://localhost:8001/process-lab-results > /tmp/upload_response.json; then
    UPLOAD_END=$(date +%s)
    UPLOAD_TIME=$((UPLOAD_END - UPLOAD_START))
    echo ""
    echo "✅ File upload test passed ($(format_time $UPLOAD_TIME))"
    echo "📊 Response preview:"
    cat /tmp/upload_response.json | head -10
    echo ""
    
    # Verify response contains expected fields
    if grep -q '"status"' /tmp/upload_response.json && \
       grep -q '"filename"' /tmp/upload_response.json && \
       grep -q '"results"' /tmp/upload_response.json; then
        echo "✅ Response contains expected fields (status, filename, results)"
    else
        echo "⚠️  Response missing expected fields"
    fi
    
    # Clean up response file
    rm -f /tmp/upload_response.json
else
    UPLOAD_END=$(date +%s)
    UPLOAD_TIME=$((UPLOAD_END - UPLOAD_START))
    echo ""
    echo "❌ File upload test failed ($(format_time $UPLOAD_TIME))"
fi

# Show container logs
echo ""
echo "📋 Container logs:"
docker logs $CONTAINER_ID

# Cleanup
echo ""
echo "🧹 Stopping and removing container..."
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID

# Calculate total time
SCRIPT_END=$(date +%s)
TOTAL_TIME=$((SCRIPT_END - SCRIPT_START))

echo ""
echo "🎉 Docker test completed!"
echo ""
echo "⏱️  Timing Summary:"
echo "   Build time: $(format_time ${BUILD_TIME:-0})"
echo "   Health check: $(format_time ${HEALTH_TIME:-0})"
echo "   File upload: $(format_time ${UPLOAD_TIME:-0})"
echo "   Total time: $(format_time $TOTAL_TIME)"
echo ""
echo "To run manually:"
echo "  docker run -p 8000:8000 \\"
echo "    -e OPENROUTER_API_KEY=your_openrouter_key \\"
echo "    -e MISTRAL_API_KEY=your_mistral_key \\"
echo "    diabetes3d-api"
