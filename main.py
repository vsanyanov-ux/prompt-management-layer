import os
import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from langfuse import Langfuse
from dotenv import load_dotenv
from mistralai import Mistral
import instructor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CorpGPT - Prompt Management Layer")

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Models from Scheme Control
class MeetingInfo(BaseModel):
    date: str = Field(description="Date of the meeting")
    time: str = Field(description="Time of the meeting")
    participants: List[str] = Field(description="List of meeting participants")
    platform: str = Field(description="Meeting platform")
    notes: Optional[str] = Field(None)
    priority: str = Field(default="normal")

@app.post("/extract")
async def extract_meeting(text: str):
    try:
        # Load prompt from Langfuse
        lf_prompt = langfuse.get_prompt("meeting_extraction", tag="production")
        
        # We use instructor with Langfuse-patched OpenAI client or just standard client
        # For simplicity in this layer, we just show how the prompt is fetched and used
        
        return {
            "success": True,
            "prompt_version": lf_prompt.versionText,
            "instructions": lf_prompt.prompt,
            "compiled_prompt": lf_prompt.compile(text=text)
        }
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import subprocess

@app.post("/webhook/langfuse")
async def langfuse_webhook(request: Request):
    """
    Endpoint to receive Langfuse webhooks.
    """
    try:
        data = await request.json()
        logger.info(f"WEBHOOK RECEIVED: {data}")
        
        event = data.get("event")
        if event in ["prompt_created", "prompt_updated"]:
            prompt_name = data.get("data", {}).get("name")
            logger.info(f"Prompt '{prompt_name}' changed. Triggering GH Actions...")
            
            # Use absolute path for gh if possible, or ensure it's in PATH
            # subprocess.Popen(["gh", "workflow", "run", "prompt_eval.yml"])
            
            # Alternative: use a more robust subprocess call
            result = subprocess.run(["gh", "workflow", "run", "prompt_eval.yml"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("GH Action triggered successfully")
                return {"status": "success"}
            else:
                logger.error(f"GH Action trigger failed: {result.stderr}")
                return {"status": "error", "detail": result.stderr}

        return {"status": "ignored", "event": event}
    except Exception as e:
        logger.error(f"WEBHOOK ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
