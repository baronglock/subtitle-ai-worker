import runpod
import subprocess
import json
import os

def handler(job):
    """Ultra simple handler that uses whisper CLI"""
    job_input = job['input']
    
    # Get file URL from your R2 storage
    file_url = f"https://{os.environ.get('R2_PUBLIC_URL')}/{job_input.get('fileName')}"
    
    # Download file
    subprocess.run(["wget", file_url, "-O", "/tmp/input.mp3"])
    
    # Run whisper (already installed in image!)
    result = subprocess.run([
        "whisper", 
        "/tmp/input.mp3",
        "--model", "base",
        "--output_format", "json",
        "--output_dir", "/tmp"
    ], capture_output=True, text=True)
    
    # Read the output
    with open("/tmp/input.json", "r") as f:
        whisper_output = json.load(f)
    
    # Format as SRT
    srt_lines = []
    for i, segment in enumerate(whisper_output.get("segments", []), 1):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        
        # Convert to SRT format
        srt_lines.append(str(i))
        srt_lines.append(f"{format_time(start)} --> {format_time(end)}")
        srt_lines.append(text.strip())
        srt_lines.append("")
    
    return {
        "transcription": whisper_output.get("text", ""),
        "srt": "\n".join(srt_lines),
        "language": whisper_output.get("language", "unknown"),
        "duration": whisper_output.get("duration", 0)
    }

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

runpod.serverless.start({"handler": handler})