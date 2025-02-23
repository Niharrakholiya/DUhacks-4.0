import os
import requests
import json
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

    def send_whatsapp_audio(self, file_path, recipient_number):
        """Send an audio file via WhatsApp Cloud API"""
        print(f"Sending audio file: {file_path} to {recipient_number}")

        # Step 1: Upload media
        upload_url = f"https://graph.facebook.com/v18.0/{self.WHATSAPP_CLOUD_NUMBER_ID}/media"
        headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}"
        }

        try:
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
                return False

            media_id = upload_response.json().get('id')
            print(f"Media ID: {media_id}")

            # Step 2: Send message
            send_url = f"https://graph.facebook.com/v18.0/{self.WHATSAPP_CLOUD_NUMBER_ID}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number,
                "type": "audio",
                "audio": {
                    "id": media_id
                }
            }
            send_response = requests.post(send_url, headers=headers, json=payload)

            if send_response.status_code == 200:
                print("Audio message sent successfully")
                return True
            else:
                print(f"Error sending audio message: {send_response.text}")
                return False

        except Exception as e:
            print(f"Error sending audio: {str(e)}")
            return False

    def process_notification(self, data):
        """Processes incoming WhatsApp notifications and handles text, audio, and image messages."""
        entries = data["entry"]
        for entry in entries:
            for change in entry["changes"]:
                value = change["value"]
                if value and "messages" in value:
                    for message in value["messages"]:
                        message_type = message["type"]
                        from_no = message["from"]

                        # Handle text messages
                        if message_type == "text":
                            message_body = message["text"]["body"]
                            print(f"Ack from FastAPI-WtsApp Webhook: {message_body}")
                            return {
                                "statusCode": 200,
                                "body": message_body,
                                "from_no": from_no,
                                "isBase64Encoded": False
                            }

                        # Handle audio messages
                        elif message_type == "audio":
                            media_id = message["audio"]["id"]
                            file_path = self.download_media(media_id, "audio", from_no)
                            if file_path:
                                print(f"Successfully downloaded audio to: {file_path}")
                                # Echo the audio back
                                if self.send_whatsapp_audio(file_path, from_no):
                                    return {
                                        "statusCode": 200,
                                        "body": "Audio received and echoed back",
                                        "from_no": from_no,
                                        "isBase64Encoded": False
                                    }
                                else:
                                    self.send_text_message("Failed to echo audio", from_no)
                                    return {
                                        "statusCode": 200,
                                        "body": "Failed to echo audio",
                                        "from_no": from_no,
                                        "isBase64Encoded": False
                                    }

                        # [Rest of the message type handlers remain the same]

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }

    # [Rest of the methods remain the same]
    def get_extension_from_mime(self, mime_type):
        """Get file extension from MIME type."""
        extension = mimetypes.guess_extension(mime_type)
        if extension:
            return extension.lstrip('.')

        # Fallback mapping for common types
        mime_map = {
            'application/pdf': 'pdf',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'audio/ogg': 'ogg',
            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
        }
        return mime_map.get(mime_type, 'bin')

    def download_media(self, media_id, media_type, phone_number, mime_type=None, filename=None):
        """Downloads media from WhatsApp Cloud API and saves it locally."""
        print(f"Downloading media ID: {media_id}, type: {media_type}, mime_type: {mime_type}")

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

                    # Determine file extension
                    if mime_type:
                        extension = self.get_extension_from_mime(mime_type)
                    elif media_type == "image":
                        extension = "jpg"
                    elif media_type == "audio":
                        extension = "ogg"
                    else:
                        extension = "bin"

                    # Use original filename if provided, otherwise generate one
                    if filename:
                        # Keep original extension if present in filename
                        base_name = os.path.splitext(filename)[0]
                        final_filename = f"media/{phone_number}_{timestamp}_{base_name}.{extension}"
                    else:
                        final_filename = f"media/{phone_number}_{timestamp}.{extension}"

                    with open(final_filename, "wb") as f:
                        f.write(media_response.content)
                    print(f"Media saved to: {final_filename}")
                    return final_filename
                else:
                    print(f"Failed to download media content: {media_response.status_code}")
            else:
                print("No URL found in media response")
        else:
            print(f"Failed to get media URL: {response.status_code}")
        return None


    # [Rest of the methods remain the same]
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
    def upload_media(self, file_path, mimet_type):
        import os
        import requests

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        url = f"{self.API_URL}/media"
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, mimet_type)}
                upload_headers = {
                    "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}"
                }
                response = requests.post(url, headers=upload_headers, files=files)

            if response.status_code == 200:
                return response.json().get('id')
            else:
                print(f"Failed to upload media: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error uploading media: {e}")
            return None


if __name__ == "__main__":
    client = WhatsAppWrapper()
    # send a template message
    client.send_template_message("hello_world", "en_US", "919574156941")
