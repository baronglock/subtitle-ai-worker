# RunPod Fix - Stop Installation Loop

## Problem
Your RunPod is installing packages EVERY request because it's not using Docker properly.

## Solution 1: Quick Fix (5 minutes)
1. Go to RunPod Dashboard
2. Select your endpoint (tvw42lbaz1cf0e)
3. Click "Edit Worker"
4. Replace handler.py with this code that auto-installs faster-whisper:

```python
import subprocess
import sys

# Install faster-whisper if not present
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Installing faster-whisper...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faster-whisper"])
    from faster_whisper import WhisperModel
```

Then add the rest of your handler code.

## Solution 2: Use Docker Image (Recommended)

### Option A: Use Pre-built Image
1. In RunPod settings, find "Container Image"
2. Change to: `runpod/whisper:base`
3. This has Whisper pre-installed!

### Option B: Build Your Own
1. Install Docker Desktop
2. Create account at hub.docker.com
3. In runpod-worker folder:

```bash
# Build image
docker build -t yourusername/subtitle-ai:latest .

# Push to Docker Hub
docker push yourusername/subtitle-ai:latest
```

4. Use `yourusername/subtitle-ai:latest` in RunPod

## Solution 3: Use RunPod Template

1. Go to RunPod Templates
2. Search "Whisper"
3. Use "Whisper ASR" template
4. Just add your handler.py

## Why This Happens

RunPod has two modes:
- **Standalone**: Runs Python directly (reinstalls every time) ❌
- **Container**: Uses Docker image (fast, cached) ✅

You're in Standalone mode, that's why it's slow!

## Test After Fix

1. Upload a small audio file
2. Should process in <30 seconds
3. No more installation logs!

## Environment Variables Needed in RunPod

Make sure these are set:
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`