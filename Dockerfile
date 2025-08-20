FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Clone repository and install Python dependencies
RUN git clone https://github.com/baronglock/subtitle-ai-worker.git /app

WORKDIR /app

# Install Python packages
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    faster-whisper

# Download Whisper model during build to cache it
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu')"

# Set the handler as the command
CMD ["python", "-u", "handler.py"]