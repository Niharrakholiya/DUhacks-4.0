from .database import (
    create_session,
    get_active_session,
    update_session_stage,
    store_user_interaction
)
from .core import transcribe_with_whisper, chat_with_memory

class MedicalSessionHandler:
    def __init__(self):
        self.welcome_message = (
            "Welcome to your medical consultation session!\n"
            "You can:\n"
            "1. Send a voice note describing your symptoms\n"
            "2. Type your symptoms as text\n"
            "I'll ask follow-up questions to better understand your condition."
        )

    def handle_message(self, phone_number, message_type, message_content):
        """Main entry point for handling messages"""
        session = get_active_session(phone_number)

        # Handle session start
        if message_content.lower().strip() == "start session":
            if not session:
                create_session(phone_number)
                return self.welcome_message
            return "You already have an active session. Please describe your symptoms."

        # Ensure active session exists
        if not session:
            return "Please type 'start session' to begin a medical consultation."

        # Handle audio or text based on message type
        if message_type == "audio":
            try:
                # The message_content should now contain the file path from WhatsApp response
                print(f"Processing audio file: {message_content}")
                # Wait for file to be saved and then transcribe
                transcript = transcribe_with_whisper(message_content)
                if not transcript:
                    return "I couldn't understand the audio. Could you please try again or type your symptoms?"
                return self._process_medical_query(phone_number, transcript)
            except Exception as e:
                print(f"Error processing audio: {e}")
                return "Sorry, I had trouble processing your voice note. Could you please try again or type your symptoms?"
        else:
            return self._process_medical_query(phone_number, message_content)

    def _process_medical_query(self, phone_number, query):
        """Process medical query and generate response"""
        try:







            return "I apologize, but I'm having trouble processing your query. Please try again."            print(f"Error processing query: {e}")        except Exception as e:            return response            update_session_stage(phone_number, "FOLLOWUP")            response = chat_with_memory(query, phone_number)
