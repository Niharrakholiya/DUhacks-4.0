from .transcription import TranscriptionService, WhisperTranscriptionService
from .storage import DataStorage, CSVStorage, VectorStorage
from .chat import ChatService, GeminiChatService
from typing import Optional, Dict, List

class MedicalSDK:
    def __init__(
        self,
        transcription_service: Optional[TranscriptionService] = None,
        storage_services: Optional[List[DataStorage]] = None,
        chat_service: Optional[ChatService] = None
    ):
        self.transcription_service = transcription_service or WhisperTranscriptionService()
        self.storage_services = storage_services or [CSVStorage(), VectorStorage()]
        self.chat_service = chat_service

    def process_audio(self, file_path: str) -> str:
        # Transcribe audio
        transcript = self.transcription_service.transcribe(file_path)

        # Store in all configured storage services
        for storage in self.storage_services:
            if isinstance(storage, CSVStorage):
                storage.store(transcript, output_file="transcription.csv")
            elif isinstance(storage, VectorStorage):
                storage.store(transcript, file_id=file_path)
            else:
                storage.store(transcript)

        return transcript

    def chat(self, query: str, context: Dict = None) -> Dict:
        if not self.chat_service:
            raise ValueError("Chat service not configured")

        context = context or {}

        # Get follow-up questions
        questions = self.chat_service.get_followup_questions(query)

        # Generate final response
        response = self.chat_service.generate_response(query, context)

        return {
            "questions": questions,
            "response": response
        }
