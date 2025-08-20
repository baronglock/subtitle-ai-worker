#!/bin/bash

echo "Starting RunPod Worker..."
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

# Pull latest code
if [ -d ".git" ]; then
    echo "Updating code from git..."
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/baronglock/subtitle-ai-worker.git .
fi

# Install requirements
echo "Installing requirements..."
pip install --no-cache-dir runpod boto3 faster-whisper

# Start the handler
echo "Starting handler..."
python -u handler.py