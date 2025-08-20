import runpod
import os

def handler(job):
    """Simple test handler to verify RunPod is working"""
    print(f"Test handler received job: {job}")
    
    job_input = job.get('input', {})
    
    # Check environment variables
    env_status = {
        "R2_ACCOUNT_ID": bool(os.environ.get('R2_ACCOUNT_ID')),
        "R2_ACCESS_KEY_ID": bool(os.environ.get('R2_ACCESS_KEY_ID')),
        "R2_SECRET_ACCESS_KEY": bool(os.environ.get('R2_SECRET_ACCESS_KEY'))
    }
    
    return {
        "status": "success",
        "message": "Test handler is working!",
        "input_received": job_input,
        "env_vars_present": env_status,
        "python_version": os.sys.version
    }

if __name__ == "__main__":
    print("Starting test handler...")
    runpod.serverless.start({"handler": handler})