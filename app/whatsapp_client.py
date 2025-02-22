# whatsapp_client.py
import os
import requests
import json
import config
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

class WhatsAppWrapper:

    API_URL = os.environ.get("WHATSAPP_API_URL")
    WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")

    def __init__(self):
            if self.API_URL is None or self.WHATSAPP_CLOUD_NUMBER_ID is None:
                raise ValueError("API_URL and WHATSAPP_CLOUD_NUMBER_ID must be set")

            self.headers = {
                "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
                "Content-Type": "application/json",
            }
            self.API_URL = str(self.API_URL) + str(self.WHATSAPP_CLOUD_NUMBER_ID)

    def download_media(self, media_id, media_type, phone_number):
        """Downloads media (image or audio) from WhatsApp Cloud API and saves it locally."""
        print(f"Downloading media ID: {media_id}, type: {media_type}")

        # Use v21.0 to match the standalone script
        media_url = f"https://graph.facebook.com/v21.0/{media_id}"
        response = requests.get(media_url, headers=self.headers)
        print(f"Media URL response: {response.status_code}")

        if response.status_code == 200:
            url = response.json().get("url")
            print(f"Media download URL: {url}")
            if url:
                media_response = requests.get(url, headers=self.headers)
                print(f"Media download response: {media_response.status_code}")
                if media_response.status_code == 200:
                    os.makedirs("media", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                    # Set extension based on media type
                    if media_type == "image":
                        extension = "jpg"
                    elif media_type == "audio":
                        extension = "ogg"  # WhatsApp voice messages are OGG
                    else:
                        extension = "bin"  # Default for unknown types

                    filename = f"media/{phone_number}_{timestamp}.{extension}"
                    with open(filename, "wb") as f:
                        f.write(media_response.content)
                    print(f"Media saved to: {filename}")
                    return filename
                else:
                    print(f"Failed to download media content: {media_response.status_code}")
            else:
                print("No URL found in media response")
        else:
            print(f"Failed to get media URL: {response.status_code}")
        return None


    def send_template_message(self, template_name, language_code, phone_number):

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }

        response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)

        assert response.status_code == 200, "Error sending message"

        return response.status_code

    def send_text_message(self,message, phone_number):
            payload = {
                "messaging_product": 'whatsapp',
                "to": phone_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)
            print(response.status_code)
            print(response.text)
            assert response.status_code == 200, "Error sending message"
            return response.status_code

    def process_notification(self, data):
        """Processes incoming WhatsApp notifications and handles text and audio messages."""
        entries = data["entry"]
        for entry in entries:
            for change in entry["changes"]:
                value = change["value"]
                if value:
                    if "messages" in value:
                        for message in value["messages"]:
                            message_type = message["type"]
                            from_no = message["from"]

                            if message_type == "text":
                                message_body = message["text"]["body"]
                                print(f"Ack from FastAPI-WtsApp Webhook: {message_body}")
                                return {
                                    "statusCode": 200,
                                    "body": message_body,
                                    "from_no": from_no,
                                    "isBase64Encoded": False
                                }
                            elif message_type == "audio":
                                media_id = message["audio"]["id"]
                                file_path = self.download_media(media_id, "audio", from_no)
                                if file_path:
                                    print(f"Successfully downloaded audio to: {file_path}")
                                    self.send_text_message("Audio received and saved!", from_no)
                                    return {
                                        "statusCode": 200,
                                        "body": "Audio received and saved",
                                        "from_no": from_no,
                                        "isBase64Encoded": False
                                    }
                                else:
                                    print("Failed to download audio")
                                    self.send_text_message("Failed to download audio", from_no)
                                    return {
                                        "statusCode": 200,
                                        "body": "Failed to download audio",
                                        "from_no": from_no,
                                        "isBase64Encoded": False
                                    }

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }

if __name__ == "__main__":
    client = WhatsAppWrapper()
    # send a template message
    client.send_template_message("hello_world", "en_US", "919574156941")
