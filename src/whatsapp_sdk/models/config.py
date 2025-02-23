from dataclasses import dataclass

@dataclass
class WhatsAppConfig:
    """Configuration class for WhatsApp SDK"""
    api_url: str
    api_token: str
    cloud_number_id: str
    webhook_token: str
