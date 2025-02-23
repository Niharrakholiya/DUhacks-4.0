class WhatsAppError(Exception):
    """Base exception for WhatsApp SDK errors"""
    pass

class MediaUploadError(WhatsAppError):
    """Raised when media upload fails"""
    pass

class MessageSendError(WhatsAppError):
    """Raised when message sending fails"""
    pass

class MediaDownloadError(WhatsAppError):
    """Raised when media download fails"""
    pass
