#!/bin/bash

# Docker Hub Push Script for Men's Health Server
# This script builds, tags, and pushes the Docker image to Docker Hub

set -e  # Exit on any error

# Configuration
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-devopswalle}"  # Your actual Docker Hub username
IMAGE_NAME="mens-health-server"
VERSION="${VERSION:-latest}"
FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "🐳 Docker Hub Push Script for Men's Health Server"
echo "=================================================="
echo "Username: ${DOCKER_HUB_USERNAME}"
echo "Image: ${IMAGE_NAME}"
echo "Version: ${VERSION}"
echo "Full image name: ${FULL_IMAGE_NAME}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if user is logged in to Docker Hub
echo "🔍 Checking Docker Hub authentication..."
if ! docker info | grep -q "Username:"; then
    echo "⚠️  You are not logged in to Docker Hub."
    echo "Please run: docker login"
    echo "Then run this script again."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Tag the image for Docker Hub
echo "🏷️  Tagging image for Docker Hub..."
docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}

# Also tag as latest if not already latest
if [ "${VERSION}" != "latest" ]; then
    docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
    echo "🏷️  Also tagged as latest"
fi

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push ${FULL_IMAGE_NAME}

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed ${FULL_IMAGE_NAME}"
else
    echo "❌ Failed to push to Docker Hub"
    exit 1
fi

# Push latest tag if we created it
if [ "${VERSION}" != "latest" ]; then
    echo "📤 Pushing latest tag..."
    docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"
    else
        echo "❌ Failed to push latest tag"
        exit 1
    fi
fi

echo ""
echo "🎉 Success! Your image is now available on Docker Hub:"
echo "   docker pull ${FULL_IMAGE_NAME}"
echo ""
echo "🔗 View on Docker Hub: https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
echo ""
echo "💡 To run the image:"
echo "   docker run -p 8004:8004 --env-file .env ${FULL_IMAGE_NAME}"