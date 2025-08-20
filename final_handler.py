#!/usr/bin/env python3
"""Final working handler - simplified and tested"""
import runpod
import os
import tempfile
import subprocess

def handler(job):
    """Simple handler that just works"""
    print("Starting job:", job)
    job_input = job['input']
    
    bucket_name = job_input.get('bucketName')
    file_name = job_input.get('fileName')
    user_plan = job_input.get('userPlan', 'free')
    
    # Select model based on plan
    model = 'medium' if user_plan == 'free' else 'large-v2'
    print(f"User plan: {user_plan}, Using model: {model}")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    input_file = os.path.join(temp_dir, "input.mp3")
    
    try:
        # Download from R2
        import boto3
        s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{os.environ.get('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY')
        )
        
        print(f"Downloading {file_name} from {bucket_name}")
        s3_client.download_file(bucket_name, file_name, input_file)
        
        # Use whisper Python API (most reliable)
        import whisper
        print(f"Loading Whisper model: {model}")
        whisper_model = whisper.load_model(model)
        
        print("Transcribing audio...")
        result = whisper_model.transcribe(input_file)
        
        # Generate SRT
        srt_lines = []
        for i, segment in enumerate(result["segments"], 1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            srt_lines.extend([str(i), f"{start} --> {end}", text, ""])
        
        return {
            "transcription": result["text"],
            "srt": "\n".join(srt_lines),
            "detected_language": result.get("language", "unknown"),
            "duration": result["segments"][-1]["end"] if result["segments"] else 0,
            "model_used": model,
            "user_plan": user_plan
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            subprocess.run(["rm", "-rf", temp_dir])

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    print("Final handler ready - Will use medium for free, large-v2 for paid")
    runpod.serverless.start({"handler": handler})