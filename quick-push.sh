#!/bin/bash

# Quick Docker Hub Login and Push
# Usage: ./quick-push.sh [version]

VERSION=${1:-latest}
DOCKER_HUB_USERNAME="devopswalle"  # Your actual Docker Hub username
IMAGE_NAME="mens-health-server"

echo "🚀 Quick push to Docker Hub"
echo "Version: $VERSION"
echo ""

# Check if logged in
if ! docker info | grep -q "Username:"; then
    echo "🔐 Logging in to Docker Hub..."
    docker login
fi

# Build, tag and push in one go
echo "🔨 Building and pushing..."
docker build -t $IMAGE_NAME:$VERSION . && \
docker tag $IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION && \
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION"
    echo "🔗 https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$IMAGE_NAME"
else
    echo "❌ Push failed"
    exit 1
fi