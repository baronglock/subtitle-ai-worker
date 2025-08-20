# RunPod Setup - Everything Pre-installed

## Option 1: Use Pre-built Whisper Image (FASTEST - NO INSTALLATION)

In your RunPod serverless configuration:

**Container Image:** `onerahmet/openai-whisper-asr-webservice:latest-gpu`

**Container Start Command:**
```bash
bash -c "pip install runpod boto3 && wget https://raw.githubusercontent.com/baronglock/subtitle-ai-worker/main/smart_handler.py -O handler.py && python handler.py"
```

This only installs 2 tiny packages (5 seconds) since Whisper is already in the image.

## Option 2: Use Official RunPod Whisper Image

**Container Image:** `runpod/whisper:latest`

**Container Start Command:**
```bash
python /app/handler.py
```

**Volume Mount:** Upload your `smart_handler.py` as `/app/handler.py`

## Option 3: Build Your Own Image (Most Control)

1. Build the Docker image:
```bash
docker build -f Dockerfile.prebuilt -t yourusername/subtitle-ai:latest .
docker push yourusername/subtitle-ai:latest
```

2. In RunPod:
- **Container Image:** `yourusername/subtitle-ai:latest`
- **Container Start Command:** (leave empty - it auto-starts)

## Environment Variables to Set in RunPod:

```
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
```

## Testing Your Setup

Once configured, your RunPod worker will:
- Start instantly (no package installation)
- Use `medium` model for free users
- Use `large-v2` GPU model for paid users
- Process and return transcriptions with SRT format

The handler automatically selects the right model based on the user's plan!