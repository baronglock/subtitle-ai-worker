#!/usr/bin/env python3
"""Universal handler that works with any Whisper installation"""
import runpod
import subprocess
import os
import json
import tempfile

def handler(job):
    """Handler that uses whisper CLI (works with any whisper image)"""
    print("Starting job:", job)
    job_input = job['input']
    
    bucket_name = job_input.get('bucketName')
    file_name = job_input.get('fileName')
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    input_file = os.path.join(temp_dir, "input.mp3")
    
    try:
        # Download from R2 using boto3
        import boto3
        s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{os.environ.get('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY')
        )
        
        print(f"Downloading {file_name} from {bucket_name}")
        s3_client.download_file(bucket_name, file_name, input_file)
        
        # Try different whisper commands based on what's available
        whisper_commands = [
            ["whisper", input_file, "--model", "base", "--output_format", "srt", "--output_dir", temp_dir],
            ["whisperx", input_file, "--model", "base", "--output_format", "srt", "--output_dir", temp_dir],
            ["python", "-m", "whisper", input_file, "--model", "base", "--output_format", "srt", "--output_dir", temp_dir]
        ]
        
        result = None
        for cmd in whisper_commands:
            try:
                print(f"Trying command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("Whisper command succeeded!")
                    break
            except:
                continue
        
        if not result or result.returncode != 0:
            # Fallback: Use Python API if available
            try:
                import whisper
                model = whisper.load_model("base")
                result_data = model.transcribe(input_file)
                
                # Generate SRT manually
                srt_lines = []
                for i, segment in enumerate(result_data["segments"], 1):
                    start = format_timestamp(segment["start"])
                    end = format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    srt_lines.extend([str(i), f"{start} --> {end}", text, ""])
                
                return {
                    "transcription": result_data["text"],
                    "srt": "\n".join(srt_lines),
                    "detected_language": result_data.get("language", "unknown"),
                    "duration": result_data["segments"][-1]["end"] if result_data["segments"] else 0
                }
            except:
                return {"error": "No working Whisper installation found"}
        
        # Read SRT file
        srt_file = input_file.replace(".mp3", ".srt")
        if os.path.exists(srt_file):
            with open(srt_file, "r") as f:
                srt_content = f.read()
        else:
            # Find any SRT file in temp dir
            for file in os.listdir(temp_dir):
                if file.endswith(".srt"):
                    with open(os.path.join(temp_dir, file), "r") as f:
                        srt_content = f.read()
                    break
            else:
                srt_content = "No SRT generated"
        
        # Extract text from SRT
        lines = srt_content.split("\n")
        text_lines = []
        for line in lines:
            if line and not line.isdigit() and "-->" not in line:
                text_lines.append(line)
        
        return {
            "transcription": " ".join(text_lines),
            "srt": srt_content,
            "detected_language": "unknown",
            "duration": 0
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            subprocess.run(["rm", "-rf", temp_dir])

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})