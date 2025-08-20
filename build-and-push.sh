#!/bin/bash

# Replace YOUR_DOCKERHUB_USERNAME with your actual Docker Hub username
DOCKER_USERNAME="YOUR_DOCKERHUB_USERNAME"
IMAGE_NAME="subtitle-ai-worker"
TAG="latest"

echo "Building Docker image..."
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$TAG .

echo "Logging in to Docker Hub..."
docker login

echo "Pushing image to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$TAG

echo "Done! Use this image in RunPod: $DOCKER_USERNAME/$IMAGE_NAME:$TAG"