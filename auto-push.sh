#!/bin/bash

# Auto Repository Creator and Push Script
# This script will guide you through creating the repository and pushing

set -e

DOCKER_HUB_USERNAME="devopswalle"
IMAGE_NAME="mens-health-server"
VERSION="latest"
REPO_URL="https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"

echo "🐳 Docker Hub Auto Setup for Men's Health Server"
echo "================================================="
echo "Username: ${DOCKER_HUB_USERNAME}"
echo "Repository: ${IMAGE_NAME}"
echo "Full name: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
echo ""

# Check if we're logged in correctly
echo "🔍 Verifying Docker Hub login..."
CURRENT_USER=$(docker info | grep -i username | awk '{print $2}' || echo "")

if [ "$CURRENT_USER" != "$DOCKER_HUB_USERNAME" ]; then
    echo "❌ Username mismatch!"
    echo "   Expected: $DOCKER_HUB_USERNAME"
    echo "   Current:  $CURRENT_USER"
    echo ""
    echo "Please run: docker logout && docker login"
    exit 1
fi

echo "✅ Logged in as $DOCKER_HUB_USERNAME"

# Build the image
echo ""
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} .

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Tag the image
echo "🏷️  Tagging image..."
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

# Check if repository exists by trying to pull (this won't work but gives us info)
echo ""
echo "🔍 Checking if repository exists..."
docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Repository exists"
else
    echo "⚠️  Repository doesn't exist yet"
    echo ""
    echo "📋 MANUAL STEP REQUIRED:"
    echo "1. Open: https://hub.docker.com/repositories"
    echo "2. Click 'Create Repository'"
    echo "3. Repository name: ${IMAGE_NAME}"
    echo "4. Description: Men's Health Server - AI-powered health assistant"
    echo "5. Visibility: Public (recommended)"
    echo "6. Click 'Create'"
    echo ""
    echo "Press ENTER after creating the repository..."
    read -r
fi

# Try to push
echo ""
echo "📤 Pushing to Docker Hub..."
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your image is now on Docker Hub!"
    echo ""
    echo "📋 Repository URL: $REPO_URL"
    echo "🚀 Pull command: docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "🔗 Next steps:"
    echo "   - View on Docker Hub: $REPO_URL"
    echo "   - Update repository description and README"
    echo "   - Set up automated builds (optional)"
    echo ""
else
    echo ""
    echo "❌ Push still failed. Possible issues:"
    echo "1. Repository not created yet - please create it manually"
    echo "2. Insufficient permissions - check your Docker Hub account"
    echo "3. Network issues - try again in a moment"
    echo ""
    echo "Manual creation URL: https://hub.docker.com/repositories"
    exit 1
fi