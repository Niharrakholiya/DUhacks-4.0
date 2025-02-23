# medical_transcription.py (Create this in root directory)

# Import pysqlite3 and replace sqlite3
__import__('sqlite3')
import sys
import os

# Update the import to use the correct path

import whisper
from pydub import AudioSegment
import csv
import chromadb
import google.generativeai as genai
import warnings
from dotenv import load_dotenv

# Load the Whisper model
model = whisper.load_model("base")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="transcriptions")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

def transcribe_with_whisper(file_path):
    """Convert audio to text using Whisper."""
    if file_path.endswith(".m4a"):
        audio = AudioSegment.from_file(file_path, format="m4a")
        temp_file_path = "temp.wav"
        audio.export(temp_file_path, format="wav")
        file_path = temp_file_path

    result = model.transcribe(file_path)

    return result["text"]

def save_transcription_to_csv(transcription, output_file="transcription.csv"):
    """Save transcription as CSV."""
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Transcription"])
        writer.writerow([transcription])

def store_in_vectordb(text, file_id):
    """Convert transcription to embedding and store in ChromaDB."""
    embedding = genai.embed_content(model="models/embedding-001", content=text)

    collection.add(
        ids=[file_id],
        embeddings=[embedding["embedding"]],
        metadatas=[{"text": text}]
    )

def retrieve_past_context(user_query):
    """Retrieve similar past transcriptions from ChromaDB."""
    query_embedding = genai.embed_content(model="models/embedding-001", content=user_query)

    results = collection.query(query_embeddings=[query_embedding["embedding"]], n_results=3)
    past_contexts = [r["text"] for r in results["metadatas"][0]] if results["metadatas"] else []

    return past_contexts

def get_followup_questions(user_query):
    """Ask necessary follow-up questions before diagnosis."""
    prompt = f"""
    The user has described the following symptom: "{user_query}".

    Before providing possible causes, recommended medicines, and precautions, generate a list of **two to three** follow-up questions that will help in better diagnosis.

    Example:
    - If the user says "I have a headache", ask:
      1. "Do you feel stressed or anxious?"
      2. "Do you have any sensitivity to light or noise?"
      3. "Have you had enough water today?"

    Now, generate follow-up questions for: "{user_query}"
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    questions = response.text.strip().split("\n") if response else []
    return [q for q in questions if q.strip()]  # Return non-empty questions

def chat_with_memory(user_query):
    """Ask follow-up questions before generating a final medical response."""
    past_contexts = retrieve_past_context(user_query)

    # Get follow-up questions
    followup_questions = get_followup_questions(user_query)

    print("\nAI: Before I analyze your symptoms, I need to ask a few questions:")
    user_responses = {}

    for question in followup_questions:
        answer = input(f"AI: {question} \nYou: ")  # Collect user response
        user_responses[question] = answer

    # Prepare final response prompt with additional details
    additional_info = "\n".join([f"{q}: {a}" for q, a in user_responses.items()])

    prompt = f"""
    You are a highly knowledgeable virtual medical assistant. Based on the user's symptoms and follow-up responses, analyze the situation and provide:

    1. **Possible Causes** - List potential reasons for the symptoms.
    2. **Recommended Medicines** - Suggest common over-the-counter or prescribed medications for symptom relief.
    3. **Precautions & Next Steps** - Advise on whether medical consultation is necessary and any home remedies.

    Previous Medical Context (if available): {past_contexts}

    **User Symptoms:** {user_query}
    **Follow-Up Responses:**
    {additional_info}

    **AI Response:**
    """

    # Use Gemini-Pro to generate final response
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text if response else "I'm sorry, I couldn't generate a response."


