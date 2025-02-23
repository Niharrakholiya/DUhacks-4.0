import requests
import pyttsx3

# API Endpoint (Replace with your actual API URL)
API_URL = "http://api.quotable.io/random"  # Example API

def fetch_text_from_api():
    """Fetch text data from an API."""
    try:
        response = requests.get(API_URL, verify=False, timeout=10)
        response.raise_for_status()  # Raise error for HTTP issues
        data = response.json()  # Parse JSON response

        print("API Response:", data)  # Debugging: Print full response

        # Ensure correct key extraction (modify if API structure is different)
        return data.get("content", "No content found in API response.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return "API request failed. Using fallback text."

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

# Fetch text from API
text = fetch_text_from_api()
print("Fetched Text:", text)

# Convert to speech with a female voice (1) and moderate speed (150)
save_speech_to_file(text, voice_id=1, rate=150)
