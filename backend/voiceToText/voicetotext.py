import whisper
from pydub import AudioSegment
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Global variable to store the model
_whisper_model = None

def get_whisper_model():
    """Load Whisper model only if not already loaded."""
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model...")
        _whisper_model = whisper.load_model("base", download_root=str(os.path.join(os.getcwd(), "models")))
        print("Whisper model loaded successfully")
    return _whisper_model

def transcribe_with_whisper(file_path):
    """Convert audio to text using Whisper."""
    # Get the model (will load only on first call)
    model = get_whisper_model()

    if file_path.endswith(".m4a"):
        audio = AudioSegment.from_file(file_path, format="m4a")
        temp_file_path = "temp.wav"
        audio.export(temp_file_path, format="wav")
        file_path = temp_file_path

    result = model.transcribe(file_path)
    return result["text"]
