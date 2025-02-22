import os
import sys
from fastapi import FastAPI, Request

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Fix import path

from app.whatsapp_client import WhatsAppWrapper  # Correct Import

app = FastAPI()

WHATSAPP_HOOK_TOKEN = os.environ.get("WHATSAPP_HOOK_TOKEN")


@app.get("/")
def i_am_alive():
    return "I am alive!!"


@app.get("/webhook/")
def subscribe(request: Request):
    print("subscribe is being called")
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if verify_token == WHATSAPP_HOOK_TOKEN:
        return int(challenge) if challenge else "No challenge found"
    
    return {"error": "Authentication failed. Invalid Token."}


@app.post("/webhook/")
async def callback(request: Request):
    print("callback is being called")
    whatsapp_client = WhatsAppWrapper()  # Use the correct class
    data = await request.json()
    print("We received:", data)

    response = whatsapp_client.process_notification(data)
    
    if response["statusCode"] == 200 and response["body"] and response["from_no"]:
        reply = response["body"]
        print("\nReply is:", reply)
        whatsapp_client.send_text_message(message=reply, phone_number=response["from_no"])
        print("\nReply sent to WhatsApp Cloud:", response)

    return {"status": "success"}