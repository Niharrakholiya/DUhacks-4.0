from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any
import os
from dotenv import load_dotenv
import logging

from src.whatsapp_sdk.client import WhatsAppClient, WhatsAppError
from examples.send_message import WhatsAppConfig

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize WhatsApp client
whatsapp_config = WhatsAppConfig(
    api_url=os.getenv("WHATSAPP_API_URL"),
    api_token=os.getenv("WHATSAPP_API_TOKEN"),
    cloud_number_id=os.getenv("WHATSAPP_CLOUD_NUMBER_ID"),
    webhook_token=os.getenv("WHATSAPP_HOOK_TOKEN")
)

whatsapp_client = WhatsAppClient(whatsapp_config)

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.get("/webhook/")
async def verify_webhook(request: Request):
    """Verify webhook endpoint for WhatsApp API"""
    try:
        verify_token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if not verify_token or not challenge:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        if verify_token != whatsapp_config.webhook_token:
            raise HTTPException(status_code=401, detail="Invalid verification token")

        return int(challenge)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid challenge value")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
