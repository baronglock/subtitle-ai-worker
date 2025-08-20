# EXACT RunPod Configuration - Copy & Paste This

## Container Configuration

**Container Image:**
```
onerahmet/openai-whisper-asr-webservice:latest-gpu
```

**Container Start Command:**
```bash
bash -c "pip install runpod boto3 && wget https://raw.githubusercontent.com/baronglock/subtitle-ai-worker/main/final_handler.py -O handler.py && python handler.py"
```

## Environment Variables (Add these in RunPod):

```
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=subtitle-ai-uploads
```

## GPU Configuration:
- Min Workers: 0
- Max Workers: 3
- GPU Type: Any available (RTX 3090, A4000, etc)
- Idle Timeout: 5 seconds
- Flash Boot: Enabled

## Testing:

1. After saving the configuration, click "Deploy"
2. Wait for "Workers Active" to show at least 1
3. Test from your website

## If Workers Don't Start:

Try this alternative image:
```
runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel
```

With this command:
```bash
bash -c "apt-get update && apt-get install -y ffmpeg && pip install runpod boto3 openai-whisper && wget https://raw.githubusercontent.com/baronglock/subtitle-ai-worker/main/final_handler.py -O handler.py && python handler.py"
```

This will take 30 seconds to start but will definitely work.