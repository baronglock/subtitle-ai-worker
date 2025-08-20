# RunPod Worker Deployment Guide

## Important: Fix for Test Handler Issue

The RunPod worker is currently using `test_handler.py` instead of the main `handler.py`. Follow these steps to deploy the correct handler:

## Option 1: Direct File Upload (Recommended for Quick Fix)

1. Go to your RunPod dashboard
2. Navigate to your serverless endpoint (ID: tvw42lbaz1cf0e)
3. Click on "Edit" or "Update Worker"
4. Upload the `handler.py` file directly (not test_handler.py)
5. Make sure the entry point is set to `handler.py`
6. Save and deploy

## Option 2: Update GitHub Repository

If you're using the GitHub repository approach:

1. Push the correct `handler.py` to your repository: https://github.com/baronglock/subtitle-ai-worker
2. Make sure `handler.py` is in the root directory
3. Remove or rename `test_handler.py` to avoid confusion
4. Update the Dockerfile if needed to ensure it's using `handler.py`

## Option 3: Create New Docker Image

1. Update the Dockerfile to copy local files instead of cloning from GitHub:

```dockerfile
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy handler file
COPY handler.py /app/handler.py

# Install Python packages
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    faster-whisper

# Download Whisper model during build to cache it
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu')"

# Set the handler as the command
CMD ["python", "-u", "handler.py"]
```

2. Build and push to Docker Hub:
```bash
docker build -t yourusername/subtitle-ai-worker:latest .
docker push yourusername/subtitle-ai-worker:latest
```

3. Update RunPod endpoint to use your new Docker image

## Environment Variables Required

Make sure these environment variables are set in RunPod:

- `R2_ACCOUNT_ID`: Your Cloudflare account ID
- `R2_ACCESS_KEY_ID`: Your R2 access key
- `R2_SECRET_ACCESS_KEY`: Your R2 secret key
- `R2_BUCKET_NAME`: Your R2 bucket name

## Testing

After deployment, test with a simple request:

```json
{
  "input": {
    "bucketName": "your-bucket-name",
    "fileName": "test-audio.mp3",
    "targetLanguage": null
  }
}
```

## Expected Response

You should receive:
```json
{
  "transcription": "The transcribed text...",
  "srt": "1\n00:00:00,000 --> 00:00:02,500\nFirst subtitle line\n\n2\n...",
  "segments": [...],
  "detected_language": "en",
  "duration": 120.5
}
```

## Troubleshooting

If you're still getting test handler responses:
1. Check RunPod logs to see which file is being executed
2. Verify the Docker image is using the correct handler
3. Ensure the environment variables are properly set
4. Try restarting the RunPod endpoint

## File Structure on RunPod

The worker should have this structure:
```
/app/
  handler.py  (main handler - use this!)
  # test_handler.py should be removed or renamed
```