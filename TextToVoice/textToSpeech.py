import requests
import pyttsx3

# API Endpoint (Replace with your actual API URL)

def save_speech_to_file(text, filename="output.mp3", voice_id=1, rate=150):
    """Convert text to speech with custom voice settings and save as an audio file."""
    engine = pyttsx3.init()

    # Get available voices
    voices = engine.getProperty("voices")
    
    # Set voice (0 = Male, 1 = Female)
    if voice_id < len(voices):
        engine.setProperty("voice", voices[voice_id].id)

    # Set speaking speed
    engine.setProperty("rate", rate)

    # Save speech to file
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    print(f"Speech saved as {filename}")



# Convert to speech with a female voice (1) and moderate speed (150)
save_speech_to_file(text, voice_id=1, rate=150)
