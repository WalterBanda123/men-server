#!/bin/bash

# Docker Hub Repository Setup and Push Script
# This script helps create the repository and push the image

set -e

# Configuration - UPDATE THESE VALUES
DOCKER_HUB_USERNAME="devopswalle"  # Your actual Docker Hub username
IMAGE_NAME="mens-health-server"
VERSION="latest"

echo "🐳 Docker Hub Repository Setup and Push"
echo "========================================"
echo "Username: ${DOCKER_HUB_USERNAME}"
echo "Repository: ${IMAGE_NAME}"
echo "Version: ${VERSION}"
echo ""

# Check Docker login status
echo "🔍 Checking Docker Hub authentication..."
if ! docker info | grep -q "Username: ${DOCKER_HUB_USERNAME}"; then
    echo "⚠️  You are not logged in as ${DOCKER_HUB_USERNAME}"
    echo "Please run: docker login"
    echo "And make sure you're using the correct username."
    exit 1
fi

echo "✅ Authenticated as ${DOCKER_HUB_USERNAME}"

# Step 1: Build the image locally
echo ""
echo "🔨 Step 1: Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "✅ Image built successfully"

# Step 2: Tag for Docker Hub
echo ""
echo "🏷️  Step 2: Tagging image for Docker Hub..."
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

# Step 3: Test the image locally (optional)
echo ""
echo "🧪 Step 3: Testing image locally (optional - press Ctrl+C to skip)..."
echo "Starting container on port 8005 for testing..."
CONTAINER_ID=$(docker run -d -p 8005:8004 --name mens-health-test ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION})

if [ $? -eq 0 ]; then
    echo "✅ Container started with ID: ${CONTAINER_ID}"
    echo "🌐 Test at: http://localhost:8005/health"
    echo ""
    echo "Press ENTER to continue with push (or Ctrl+C to stop and troubleshoot)..."
    read -r
    
    # Clean up test container
    echo "🧹 Cleaning up test container..."
    docker stop ${CONTAINER_ID} > /dev/null 2>&1
    docker rm ${CONTAINER_ID} > /dev/null 2>&1
else
    echo "⚠️  Container failed to start, but continuing with push..."
fi

# Step 4: Push to Docker Hub
echo ""
echo "📤 Step 4: Pushing to Docker Hub..."
echo "This may take a few minutes..."

# First attempt - try to push
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your image has been pushed to Docker Hub!"
    echo ""
    echo "📋 Your image is now available at:"
    echo "   docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "🔗 View on Docker Hub:"
    echo "   https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
    echo ""
    echo "🚀 To run your image anywhere:"
    echo "   docker run -p 8004:8004 --env-file .env ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
    
else
    echo ""
    echo "❌ Push failed. This could be due to:"
    echo ""
    echo "1. Repository doesn't exist on Docker Hub:"
    echo "   - Go to https://hub.docker.com/repositories"
    echo "   - Click 'Create Repository'"
    echo "   - Name: ${IMAGE_NAME}"
    echo "   - Set to Public or Private"
    echo "   - Then run this script again"
    echo ""
    echo "2. Username mismatch:"
    echo "   - Your Docker Hub username might not be '${DOCKER_HUB_USERNAME}'"
    echo "   - Check your username at https://hub.docker.com/settings/general"
    echo "   - Update the DOCKER_HUB_USERNAME in this script"
    echo ""
    echo "3. Authentication issue:"
    echo "   - Run: docker logout && docker login"
    echo "   - Then run this script again"
    echo ""
    exit 1
fi