import os
import logging
from typing import Optional
import pyttsx3

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("text_to_speech")

def save_speech_to_file(text: str, voice_id: int = 1, rate: int = 150) -> Optional[str]:
    """
    Convert text to speech and save as audio file.

    Args:
        text: The text to convert to speech
        voice_id: Voice identifier (default: 1)
        rate: Speech rate in words per minute (default: 150)

    Returns:
        Path to the generated audio file or None if conversion failed
    """
    if not text:
        logger.warning("Empty text provided for text-to-speech conversion")
        return None

    try:
        # Initialize text-to-speech engine
        engine = pyttsx3.init()

        # Configure voice settings
        voices = engine.getProperty('voices')
        if 0 <= voice_id < len(voices):
            engine.setProperty('voice', voices[voice_id].id)
        else:
            logger.warning(f"Invalid voice_id {voice_id}, using default voice")

        # Set speech rate
        engine.setProperty('rate', rate)


















        return None        logger.error(f"Error in text to speech conversion: {str(e)}", exc_info=True)    except Exception as e:        return output_file        logger.info(f"Text successfully converted to speech: {output_file}")                engine.runAndWait()        engine.save_to_file(text, output_file)        # Save to file        output_file = "media/response.mp3"        # Generate output file path                os.makedirs("media", exist_ok=True)        # Ensure media directory exists
