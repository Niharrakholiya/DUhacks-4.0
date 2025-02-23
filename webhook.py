import json
import os
import sys
from fastapi import FastAPI, Request
from typing import Optional, Dict, Any
from datetime import datetime

from app.whatsapp_client import WhatsAppWrapper
from database import *
from database import update_acknowledgment
from database import get_unacknowledged_messages
from database import store_user_interaction
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

async def retry_unacknowledged_messages(whatsapp_client: WhatsAppWrapper, phone_number: str):
    """Retry sending unacknowledged messages to the user"""
    unack_messages = get_unacknowledged_messages(phone_number)

    if not unack_messages:
        return None

    print(f"[Retry] Found {len(unack_messages)} unacknowledged messages")

    for message in unack_messages:
        try:
            # Send the pending message
            whatsapp_client.send_text_message(
                message=message['response'],
                phone_number=phone_number
            )
            print(f"[Retry] Resent message ID: {message['id']}")

            # Update acknowledgment status
            update_acknowledgment(message['id'])

        except Exception as e:
            print(f"[Error] Failed to resend message {message['id']}: {str(e)}")
            continue

    return {
        "status": "success",
        "action": "resent_messages",
        "count": len(unack_messages)
    }


def safe_get_message_info(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely extract message information from WhatsApp webhook payload.
    Returns message ID, type, and status if available.
    """
    try:
        if 'entry' in data and data['entry'] and 'changes' in data['entry'][0]:
            value = data['entry'][0]['changes'][0].get('value', {})

            # Handle status updates
            if 'statuses' in value and value['statuses']:
                status_data = value['statuses'][0]
                return {
                    'message_id': status_data.get('id'),
                    'recipient_id': status_data.get('recipient_id'),
                    'status': status_data.get('status'),
                    'type': 'status'
                }

            # Handle incoming messages
            if 'messages' in value and value['messages']:
                message_data = value['messages'][0]
                return {
                    'message_id': message_data.get('id'),
                    'from_number': message_data.get('from'),
                    'text': message_data.get('text', {}).get('body', ''),
                    'type': 'message'
                }
        return None
    except (KeyError, IndexError):
        return None

@app.post("/webhook/")
async def callback(request: Request):
    print("callback is being called")
    whatsapp_client = WhatsAppWrapper()
    data = await request.json()
    print("\n\n\n\n")
    print("Received webhook data:", json.dumps(data, indent=2))
    print("\n\n\n\n")
    message_info = safe_get_message_info(data)
    if not message_info:
        return {"status": "ignored", "reason": "Invalid payload structure"}

    # Handle status updates
    # if message_info['type'] == 'status':
    #     if message_info['status'] in ['delivered', 'read']:
    #         update_acknowledgment(message_info['message_id'])
    #         return {"status": "success", "action": "status_updated"}

    # Handle incoming messages
    elif message_info['type'] == 'message':
        phone_number = message_info['from_number']
        query = message_info['text']
        message_id = message_info['message_id']  # Get message_id from the payload

        # Check for unacknowledged messages first
        # unack_messages = get_unacknowledged_messages(phone_number)
        # if unack_messages:
        #     print(f"Found {len(unack_messages)} unacknowledged messages")
        #     retry_response = await retry_unacknowledged_messages(whatsapp_client, phone_number)
        #     if retry_response:
        #         return retry_response
            # return {"status": "ignored", "reason": "Pending acknowledgments"}

        # Process new message
        response = whatsapp_client.process_notification(data)

        if response["statusCode"] == 200 and response["body"] and response["from_no"]:
            reply = response["body"]
        
            # Store interaction in database with message_id
            stored_id = store_user_interaction(
                phone_number=phone_number,
                query=query,
                response=reply,
                message_id=message_id,  # Pass the message_id here
                embedding=None
            )

            if stored_id:
                # Send response
                print(f"\nSending reply: {reply}")
                whatsapp_client.send_text_message(
                    message=reply,
                    phone_number=response["from_no"]
                )
                print(f"\nReply sent to WhatsApp Cloud: {response}")

                return {
                    "status": "success",
                    "action": "message_processed",
                    "message_id": message_id
                }
            else:
                return {
                    "status": "ignored",
                    "reason": "Message already processed"
                }

    return {"status": "success"}
