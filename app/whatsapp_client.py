import os
import sys
import requests
import json
import mimetypes
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from database import update_user_interaction
from backend.Medical.medical_assistant import MedicalAssistantSDK
from backend.voiceToText.voicetotext import transcribe_with_whisper

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
        """Enhanced notification processing for all media types"""
        print(f"We received: {data}")
        entries = data["entry"]
        for entry in entries:
            for change in entry["changes"]:
                value = change["value"]
                if value and "messages" in value:
                    for message in value["messages"]:
                        message_type = message["type"]
                        from_no = message["from"]

                        # Handle different message types
                        if message_type == "text":
                            return self._handle_text_message(message, from_no)
                        if message_type == "audio":
                            return self._handle_media_message("audio", message, from_no)
                        elif message_type in ["image", "audio", "document", "video"]:
                            return {
                                "statusCode": 200,
                                "body": f"{message_type} is not supported yet",
                                "from_no": from_no,
                                "isBase64Encoded": False
                            }

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }

    def _handle_text_message(self, message, from_no):
        """Handle text messages"""
        message_body = message["text"]["body"]
        print(f"Received text message: {message_body}")

        res=MedicalAssistantSDK().get_medical_advice(message_body)
        # save_speech_to_file(res,voice_id=1, rate=150)
        return {
            "statusCode": 200,
            "body": res,
            "from_no": from_no,
            "isBase64Encoded": False
        }

    def _handle_media_message(self, message_type, message, from_no):
        """Handle all media type messages"""
        try:
            media_info = message.get(message_type, {})
            media_id = media_info.get("id")
            mime_type = media_info.get("mime_type")

            print(f"Processing {message_type} with ID: {media_id}, MIME: {mime_type}")

            file_path = self.download_media(
                media_id=media_id,
                media_type=message_type,
                phone_number=from_no,
                mime_type=mime_type
            )

            if file_path:


                transcript = transcribe_with_whisper(file_path)
                res=MedicalAssistantSDK().get_medical_advice(transcript)
                # save_transcription_to_csv(transcript)
                # store_in_vectordb(transcript, file_id=file_path)
                # print("\nTranscription stored in VectorDB ✅")
                # response = chat_with_memory(transcript)
                # print("\nChatbot Response:", response)

                return {
                    "statusCode": 200,
                    "body": res,
                    "file_path": file_path,
                    "from_no": from_no,
                    "isBase64Encoded": False,
                    "update_it": True
                }
                # Send appropriate confirmation message
                media_type_msg = {
                    "image": "Image",
                    "audio": "Voice message",
                    "document": "Document",
                    "video": "Video"
                }.get(message_type, "File")

                # self.send_text_message(f"{media_type_msg} received and saved!", from_no)
                return {
                    "statusCode": 200,
                    "body": f"{media_type_msg} received and saved",
                    "from_no": from_no,
                    "file_path": file_path,
                    "isBase64Encoded": False
                }
            else:
                error_msg = f"Failed to process {message_type}"
                self.send_text_message(f"Sorry, {error_msg}", from_no)
                return {
                    "statusCode": 500,
                    "body": error_msg,
                    "from_no": from_no,
                    "isBase64Encoded": False
                }

        except Exception as e:
            error_msg = f"Error processing {message_type}: {str(e)}"
            print(error_msg)
            self.send_text_message(f"Sorry, failed to process your {message_type}", from_no)
            return {
                "statusCode": 500,
                "body": error_msg,
                "from_no": from_no,
                "isBase64Encoded": False
            }

    def get_extension_from_mime(self, mime_type):
        """Enhanced MIME type detection with fixed audio handling"""
        # First try mimetypes
        extension = mimetypes.guess_extension(mime_type)
        if extension:
            return extension.lstrip('.')

        # Enhanced MIME type mapping with OGG as default audio format
        mime_map = {
            'application/pdf': 'pdf',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/webp': 'webp',
            'image/gif': 'gif',
            'audio/ogg': 'ogg',
            'audio/opus': 'ogg',  # WhatsApp voice messages often use opus codec
            'audio/mpeg': 'ogg',  # Convert to ogg for consistency
            'audio/mp3': 'ogg',   # Convert to ogg for consistency
            'audio/wav': 'ogg',   # Convert to ogg for consistency
            'audio/aac': 'ogg',   # Convert to ogg for consistency
            'video/mp4': 'mp4',
            'video/3gpp': '3gp',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'application/vnd.ms-powerpoint': 'ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
            'text/plain': 'txt',
            'application/zip': 'zip',
            'application/x-rar-compressed': 'rar'
        }

        # Type-specific fallbacks - Updated for WhatsApp audio
        if mime_type:
            if mime_type.startswith('audio/'):
                return 'ogg'  # Always default to ogg for audio
            elif mime_type.startswith('image/'):
                return 'jpg'
            elif mime_type.startswith('video/'):
                return 'mp4'
            elif mime_type.startswith('application/'):
                return 'pdf'

        return mime_map.get(mime_type, 'bin')

    def download_media(self, media_id, media_type, phone_number, mime_type=None, filename=None):
        """Enhanced media download with better logging"""
        print(f"Starting download for media ID: {media_id}, type: {media_type}, mime: {mime_type}")

        # Step 1: Get media URL
        media_url = f"https://graph.facebook.com/v21.0/{media_id}"
        try:
            response = requests.get(media_url, headers=self.headers)
            print(f"Media URL fetch response: {response.status_code}")

            if response.status_code != 200:
                print(f"Error response: {response.text}")
                return None

            url = response.json().get("url")
            if not url:
                print("No URL in response")
                return None

            print(f"Got download URL for media")

            # Step 2: Download media content
            media_response = requests.get(url, headers=self.headers)
            if media_response.status_code != 200:
                print(f"Failed to download media: {media_response.status_code}")
                return None

            # Step 3: Determine extension
            if not mime_type:
                type_to_ext = {
                    "image": "jpg",
                    "audio": "ogg",
                    "video": "mp4",
                    "document": "pdf"
                }
                extension = type_to_ext.get(media_type, "bin")
            else:
                extension = self.get_extension_from_mime(mime_type)

            # Step 4: Create filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            if filename:
                base_name = os.path.splitext(filename)[0]
                final_filename = f"media/{phone_number}_{timestamp}_{base_name}.{extension}"
            else:
                final_filename = f"media/{phone_number}_{timestamp}.{extension}"

            # Step 5: Save file
            os.makedirs("media", exist_ok=True)
            with open(final_filename, "wb") as f:
                f.write(media_response.content)
            print(f"Successfully saved media to: {final_filename}")
            return final_filename

        except Exception as e:
            print(f"Error in download_media: {str(e)}")
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
