from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import logging
from datetime import datetime
from pathlib import Path

from .exceptions import WhatsAppError, MediaUploadError, MediaDownloadError
from .models.messages import MessageResponse

logger = logging.getLogger(__name__)

class IWhatsAppClient(ABC):
    @abstractmethod
    def send_text_message(self, to: str, message: str) -> MessageResponse:
        pass

    @abstractmethod
    def send_audio_message(self, to: str, file_path: str) -> MessageResponse:
        pass

    @abstractmethod
    def send_template_message(self, to: str, template_name: str, language_code: str) -> MessageResponse:
        pass

class WhatsAppClient(IWhatsAppClient):
    def __init__(self, config):
        self.config = config
        self.base_url = f"{config.api_url}{config.cloud_number_id}"
        self.headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
        }

    # ...rest of the WhatsAppClient implementation...
    # Copy the methods from the original implementation while maintaining
    # the interface defined in IWhatsAppClient
