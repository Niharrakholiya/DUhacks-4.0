from logging import log
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_whatsapp_audio(file_path, recipient_number):
    """
    Send an audio file via WhatsApp Cloud API

    Args:
        file_path (str): Path to the audio file (.ogg format)
        recipient_number (str): Recipient's phone number
    """
    phone_number_id = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")
    access_token = os.environ.get("WHATSAPP_API_TOKEN")

    # Step 1: Upload media
    upload_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/media"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    with open(file_path, 'rb') as f:
        files = {
            'file': (os.path.basename(file_path), f, 'audio/ogg')
        }
        data = {
            'messaging_product': 'whatsapp'
        }
        upload_response = requests.post(upload_url, headers=headers, files=files, data=data)

    if upload_response.status_code != 200:
        print(f"Error uploading media: {upload_response.text}")
        return

    media_id = upload_response.json().get('id')
    print(f"Media ID: {media_id}")

    # Step 2: Send message
    send_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",  # Fixed: messenger_product -> messaging_product
        "to": recipient_number,
        "type": "audio",  # Fixed: image -> audio
        "audio": {  # Fixed: image -> audio
            "id": media_id
        }
    }

    send_response = requests.post(send_url, headers=headers, json=payload)

    if send_response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Error sending message: {send_response.text}")

if __name__ == "__main__":
    file_path = "media/919574156941_20250223015518.ogg"
    recipient_number = "919574156941"
    send_whatsapp_audio(file_path, recipient_number)
