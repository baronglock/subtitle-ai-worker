#!/usr/bin/env python3
"""Smart handler that selects Whisper model based on user plan"""
import runpod
import os
import json
import tempfile
import subprocess

def handler(job):
    """Handler that selects model quality based on user plan"""
    print("Starting job:", job)
    job_input = job['input']
    
    bucket_name = job_input.get('bucketName')
    file_name = job_input.get('fileName')
    user_plan = job_input.get('userPlan', 'free')  # Get user plan from request
    
    # Select Whisper model based on plan
    # Free plan gets medium quality (good accuracy)
    # Paid plans get large-v2 on GPU (fastest + best quality)
    model_selection = {
        'free': 'medium',        # Good quality for free users
        'starter': 'large-v2',   # Best model, GPU accelerated
        'pro': 'large-v2',       # Best model, GPU accelerated
        'enterprise': 'large-v2' # Best model, GPU accelerated
    }
    
    selected_model = model_selection.get(user_plan, 'medium')
    print(f"User plan: {user_plan}, Using model: {selected_model}")
    
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
        
        # Check if we have faster-whisper (better) or regular whisper
        try:
            from faster_whisper import WhisperModel
            print(f"Using faster-whisper with {selected_model} model")
            
            # Faster-whisper is MUCH faster and uses less memory
            model = WhisperModel(selected_model, device="cuda", compute_type="float16")
            segments, info = model.transcribe(input_file, beam_size=5)
            
            # Convert to list
            segments_list = list(segments)
            
            # Generate SRT
            srt_lines = []
            full_text = []
            for i, segment in enumerate(segments_list, 1):
                start = format_timestamp(segment.start)
                end = format_timestamp(segment.end)
                text = segment.text.strip()
                
                srt_lines.extend([str(i), f"{start} --> {end}", text, ""])
                full_text.append(text)
            
            processing_info = {
                "model_used": f"faster-whisper/{selected_model}",
                "user_plan": user_plan,
                "processing_speed": "fast",
                "quality": get_quality_description(selected_model)
            }
            
            return {
                "transcription": " ".join(full_text),
                "srt": "\n".join(srt_lines),
                "detected_language": info.language,
                "duration": info.duration,
                "processing_info": processing_info
            }
            
        except ImportError:
            print(f"Faster-whisper not available, using OpenAI Whisper")
            
            # Fallback to regular whisper
            import whisper
            model = whisper.load_model(selected_model)
            result = model.transcribe(input_file)
            
            # Generate SRT
            srt_lines = []
            for i, segment in enumerate(result["segments"], 1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                srt_lines.extend([str(i), f"{start} --> {end}", text, ""])
            
            processing_info = {
                "model_used": f"openai-whisper/{selected_model}",
                "user_plan": user_plan,
                "processing_speed": "standard",
                "quality": get_quality_description(selected_model)
            }
            
            return {
                "transcription": result["text"],
                "srt": "\n".join(srt_lines),
                "detected_language": result.get("language", "unknown"),
                "duration": result["segments"][-1]["end"] if result["segments"] else 0,
                "processing_info": processing_info
            }
        
    except Exception as e:
        print(f"Error: {str(e)}")
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

def get_quality_description(model):
    """Get quality description for each model"""
    descriptions = {
        'tiny': 'Basic quality - Fast processing',
        'base': 'Good quality - Balanced speed',
        'small': 'High quality - Slower processing',
        'medium': 'Premium quality - Professional results',
        'large': 'Maximum quality - Studio grade',
        'large-v2': 'Ultra HD quality - GPU accelerated, fastest & most accurate'
    }
    return descriptions.get(model, 'Standard quality')

if __name__ == "__main__":
    print("Smart handler ready - Model selection based on user plan")
    print("Free: medium | Paid plans: large-v2 (GPU accelerated)")
    runpod.serverless.start({"handler": handler})