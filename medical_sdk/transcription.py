from abc import ABC, abstractmethod
import whisper
from pydub import AudioSegment

class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, file_path: str) -> str:
        pass

class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, file_path: str) -> str:
        if file_path.endswith(".m4a"):
            audio = AudioSegment.from_file(file_path, format="m4a")
            temp_file_path = "temp.wav"
            audio.export(temp_file_path, format="wav")
            file_path = temp_file_path

        result = self.model.transcribe(file_path)
        return result["text"]
