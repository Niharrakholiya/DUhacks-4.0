import os
from dotenv import load_dotenv
from whatsapp_sdk import WhatsAppClient, WhatsAppConfig

# Load environment variables
load_dotenv()

def main():
    # Initialize WhatsApp client
    config = WhatsAppConfig(
        api_url=os.getenv("WHATSAPP_API_URL"),
        api_token=os.getenv("WHATSAPP_API_TOKEN"),
        cloud_number_id=os.getenv("WHATSAPP_CLOUD_NUMBER_ID"),
        webhook_token=os.getenv("WHATSAPP_HOOK_TOKEN")
    )

    client = WhatsAppClient(config)

    # Example: Send text message
    response = client.send_text_message(
        to="1234567890",
        message="Hello from WhatsApp SDK!"
    )
    print(f"Message sent with status: {response.status_code}")

if __name__ == "__main__":
    main()
