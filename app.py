# Import pysqlite3 and replace sqlite3
import sqlite3
import sys


import os
import sys

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Update the import to use the correct path
from app.whatsapp_client import WhatsAppWrapper

import whisper
from pydub import AudioSegment
import csv

# Workaround for SQLite compatibility

import chromadb
import google.generativeai as genai
import json
import warnings
import os
from dotenv import load_dotenv

from database import init_db, store_user_interaction, get_user_history, search_similar_queries

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

# Initialize database at startup
init_db()

def transcribe_with_whisper(file_path):
    """Convert audio to text using Whisper."""
    if file_path.endswith(".m4a"):
        audio = AudioSegment.from_file(file_path, format="m4a")
        temp_file_path = "temp.wav"
        audio.export(temp_file_path, format="wav")
        file_path = temp_file_path

    result = model.transcribe(file_path)
    whatsappclient = WhatsAppWrapper()
    whatsappclient.send_text_message(message=result["text"], phone_number="919574156941")
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

def chat_with_memory(user_query, phone_number="919574156941"):
    """Modified chat function with database integration"""
    # Get user's history
    user_history = get_user_history(phone_number)

    # Generate embedding for current query
    query_embedding = genai.embed_content(
        model="models/embedding-001",
        content=user_query
    )["embedding"]

    # Get follow-up questions
    followup_questions = get_followup_questions(user_query)

    print("\nAI: Before I analyze your symptoms, I need to ask a few questions:")
    user_responses = {}

    for question in followup_questions:
        answer = input(f"AI: {question} \nYou: ")
        user_responses[question] = answer

    # Include user history in prompt
    history_context = "\n".join([
        f"Previous Query: {h['query']}\nResponse: {h['response']}"
        for h in user_history[:2]  # Only use last 2 interactions
    ])

    # Prepare final response prompt
    prompt = f"""
    Previous History:
    {history_context}

    Current Query: {user_query}
    Follow-up Responses:
    {json.dumps(user_responses, indent=2)}

    Please provide medical advice considering the user's history and current symptoms.
    """

    # Generate response
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    response_text = response.text if response else "I'm sorry, I couldn't generate a response."

    # Store interaction in database
    store_user_interaction(
        phone_number=phone_number,
        query=user_query,
        response=response_text,
        embedding=query_embedding
    )

    return response_text

# ===== RUN TRANSCRIPTION & STORE IN VECTOR DB =====
file_path = "media/919574156941_20250223114730.ogg"  # Replace with your file
transcript = transcribe_with_whisper(file_path)
print("\nTranscription:", transcript)

# Save transcription locally
save_transcription_to_csv(transcript)

# Store in VectorDB
store_in_vectordb(transcript, file_id=file_path)

print("\nTranscription stored in VectorDB ✅")

# ===== INTERACTIVE CHAT SESSION =====
response = chat_with_memory(transcript)
print("\nChatbot Response:", response)
