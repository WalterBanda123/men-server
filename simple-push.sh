#!/bin/bash

# Simple Build and Push Script
# This script builds and pushes without complex checks

set -e

DOCKER_HUB_USERNAME="devopswalle"
IMAGE_NAME="mens-health-server"
VERSION="latest"

echo "🐳 Building and Pushing Men's Health Server"
echo "==========================================="
echo "Target: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""

# Build the image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} .

# Tag for Docker Hub
echo "🏷️  Tagging for Docker Hub..."
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
echo "If this fails, you need to create the repository first at:"
echo "https://hub.docker.com/repositories"
echo ""

docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Image pushed to Docker Hub!"
    echo ""
    echo "🎯 Your image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo "📋 Pull command: docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo "🔗 View at: https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo "Create repository at: https://hub.docker.com/repositories"
    echo "Repository name: ${IMAGE_NAME}"
    echo "Then run this script again."
fi