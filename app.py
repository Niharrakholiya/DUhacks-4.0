import os
import ssl
from dotenv import load_dotenv
from medical_sdk.client import MedicalSDK
from medical_sdk.chat import GeminiChatService
from app.whatsapp_client import WhatsAppWrapper
from database import init_db, store_user_interaction, get_user_history

# SSL Certificate verification bypass (if needed)
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize WhatsApp client
whatsapp_client = WhatsAppWrapper()

# Initialize the Medical SDK
sdk = MedicalSDK(
    chat_service=GeminiChatService(api_key=GEMINI_API_KEY)
)

# Initialize database
init_db()

def process_medical_query(file_path: str, phone_number: str = "919574156941"):
    """Process audio file and generate medical response"""

    # Step 1: Transcribe and store audio
    transcript = sdk.process_audio(file_path)
    print("\nTranscription:", transcript)

    # Send transcription to user via WhatsApp
    whatsapp_client.send_text_message(
        message=f"I heard: {transcript}",
        phone_number=phone_number
    )

    # Get user history
    user_history = get_user_history(phone_number)
    history_context = "\n".join([
        f"Previous Query: {h['query']}\nResponse: {h['response']}"
        for h in user_history[:2]
    ])

    # Chat with context
    chat_response = sdk.chat(
        query=transcript,
        context={
            "history": history_context,
            "followup_responses": {}  # You could implement a way to get user responses to follow-up questions
        }
    )

    # Store the interaction
    store_user_interaction(
        phone_number=phone_number,
        query=transcript,
        response=chat_response["response"],
        embedding=None  # You might want to add embedding functionality to the SDK
    )

    # Send response via WhatsApp
    whatsapp_client.send_text_message(
        message="\n\nFollow-up questions:\n" + "\n".join(chat_response["questions"]) +
                "\n\nResponse:\n" + chat_response["response"],
        phone_number=phone_number
    )

    return chat_response

if __name__ == "__main__":
    # Example usage
    file_path = "media/919574156941_20250223165453.m4a"
    response = process_medical_query(file_path)
    print("\nFollow-up questions:", response["questions"])
    print("\nChatbot Response:", response["response"])
