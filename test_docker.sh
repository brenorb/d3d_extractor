#!/bin/bash

echo "🐳 Docker Container Test Script"
echo "================================"

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

# Build the image
echo ""
echo "🔨 Building Docker image..."
if docker build -t diabetes3d-api .; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Test the container
echo ""
echo "🚀 Starting container..."
CONTAINER_ID=$(docker run -d -p 8001:8000 \
    -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-dummy_key}" \
    diabetes3d-api)

if [ $? -eq 0 ]; then
    echo "✅ Container started with ID: $CONTAINER_ID"
else
    echo "❌ Failed to start container"
    exit 1
fi

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 10

# Test health endpoint
echo ""
echo "🔍 Testing health endpoint..."
if curl -f http://localhost:8001/health; then
    echo ""
    echo "✅ Health check passed"
else
    echo ""
    echo "❌ Health check failed"
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

echo ""
echo "🎉 Docker test completed!"
echo ""
echo "To run manually:"
echo "  docker run -p 8000:8000 -e OPENROUTER_API_KEY=your_key diabetes3d-api"
