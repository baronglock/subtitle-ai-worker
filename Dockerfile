FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel

# Install system dependencies ONCE
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install ALL Python packages ONCE
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    faster-whisper

# Clone your repository ONCE
RUN git clone https://github.com/baronglock/subtitle-ai-worker.git /app

WORKDIR /app

# Download Whisper model during build to cache it
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu')"

# Just run the handler - NO INSTALLATION!
CMD ["python", "-u", "handler.py"]