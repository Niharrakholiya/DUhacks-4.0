from medical_sdk.client import MedicalSDK
from medical_sdk.chat import GeminiChatService
import os

# Initialize SDK
sdk = MedicalSDK(
    chat_service=GeminiChatService(api_key=os.getenv("GEMINI_API_KEY"))
)

# Process audio file
transcript = sdk.process_audio("media/919574156941_20250223165453.m4a")

# Chat with context
response = sdk.chat(
    query=transcript,
    context={
        "history": "Previous interactions...",
        "followup_responses": {"Question 1": "Answer 1"}
    }
)

print("Follow-up questions:", response["questions"])
print("Final response:", response["response"])
