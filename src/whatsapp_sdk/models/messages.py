from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    TEMPLATE = "template"

@dataclass
class MessageResponse:
    status_code: int
    message_id: Optional[str]
    timestamp: datetime
    error: Optional[str] = None
