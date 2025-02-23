from abc import ABC, abstractmethod
import csv
import chromadb
import google.generativeai as genai

class DataStorage(ABC):
    @abstractmethod
    def store(self, data: str, **kwargs):
        """Store data with optional parameters"""
        pass

class CSVStorage(DataStorage):
    def store(self, data: str, **kwargs):
        output_file = kwargs.get('output_file', "transcription.csv")
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Transcription"])
            writer.writerow([data])

class VectorStorage(DataStorage):
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "transcriptions"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def store(self, data: str, **kwargs):
        file_id = kwargs.get('file_id', str(hash(data)))  # Use hash as default ID if none provided
        embedding = genai.embed_content(model="models/embedding-001", content=data)
        self.collection.add(
            ids=[file_id],
            embeddings=[embedding["embedding"]],
            metadatas=[{"text": data}]
        )
