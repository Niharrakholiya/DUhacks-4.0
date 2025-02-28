import os
import ssl
import warnings
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# SSL workaround for macOS
ssl._create_default_https_context = ssl._create_unverified_context

class MedicalAssistantSDK:
    """
    Simple SDK for medical assistant functionality using Google's Gemini API.
    Implemented as a Singleton to prevent multiple instances.
    """
    # Singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of MedicalAssistantSDK exists.
        """
        if cls._instance is None:
            cls._instance = super(MedicalAssistantSDK, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Medical Assistant SDK if not already initialized.

        Args:
            api_key (str, optional): Gemini API key. If not provided, will attempt to load from .env file
        """
        # Only initialize once
        if getattr(self, '_initialized', False):
            return

        # Load from provided API key or environment
        if api_key:
            self.api_key = api_key
        else:
            load_dotenv()
            self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("API key is required. Provide it as a parameter or set GEMINI_API_KEY in your .env file.")

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Default model
        self.model_name = "gemini-2.0-flash-lite"

        # Mark as initialized
        self._initialized = True

    def set_model(self, model_name: str) -> None:
        """
        Set model to use for medical advice.

        Args:
            model_name (str): The name of the Gemini model to use
        """
        self.model_name = model_name

    def get_medical_advice(self, symptoms: str) -> str:
        """
        Get medical advice based on user-provided symptoms.

        Args:
            symptoms (str): Description of symptoms from the user

        Returns:
            str: Medical advice response from the AI
        """
        prompt = f"""
        You are स्वास्थ्यमित्र (Swasthya-Mitra), a caring virtual medical assistant. Based on the symptoms, provide a clear analysis:

        🏥 Medical Analysis for: "{symptoms}"

        Please provide your response in this format:

        🔍 Possible Causes:
        • List 2-3 most likely causes
        • Keep explanations brief and clear

        💊 Recommended Relief Measures:
        • Suggest safe over-the-counter medications
        • Include dosage guidelines
        • List natural home remedies

        ⚠️ Important Precautions:
        • Mention when to seek immediate medical help
        • List key warning signs
        • Provide lifestyle recommendations

        IMPORTANT INSTRUCTIONS:
        1. Format the response with bullet points and emojis
        2. Keep it concise and easy to read
        3. Do NOT include any disclaimer at the end
        4. Do NOT include statements like "consult a doctor" or "this is not medical advice"
        5. Do NOT include any closing message like "take care" or "hope you feel better"
        6. End your response immediately after the Important Precautions section

        User Symptoms: {symptoms}

        Response:
        """

        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)

        text = response.text if response else "I'm sorry, I couldn't generate a response."

        # Backup method: Clean any disclaimer that might be generated despite instructions
        if "professional medical advice" in text.lower() or "consult a doctor" in text.lower():
            # Find the last occurrence of an emoji indicating the end of content
            emoji_positions = [text.rfind("⚠️"), text.rfind("💊"), text.rfind("🔍")]
            valid_positions = [pos for pos in emoji_positions if pos != -1]

            if valid_positions:
                # Find the paragraph break after the last emoji section
                last_section_start = max(valid_positions)
                sections = text[last_section_start:].split("\n\n")
                if len(sections) > 1:
                    # Keep everything before the final paragraph (which might contain disclaimer)
                    text = text[:last_section_start] + sections[0]

        return text

