# WhatsApp SDK API Documentation

## Class Diagram
```mermaid
classDiagram
    class IWhatsAppClient {
        <<interface>>
        +send_text_message(to: str, message: str)
        +send_audio_message(to: str, file_path: str)
        +send_template_message(to: str, template: str, lang: str)
    }

    class WhatsAppClient {
        -config: WhatsAppConfig
        -headers: Dict
        +send_text_message()
        +send_audio_message()
        +send_template_message()
        +process_webhook()
        -_handle_media_message()
        -_handle_text_message()
    }

    class WhatsAppConfig {
        +api_url: str
        +api_token: str
        +cloud_number_id: str
        +webhook_token: str
    }

    class MessageResponse {
        +status_code: int
        +message_id: str
        +timestamp: datetime
        +error: Optional[str]
    }

    IWhatsAppClient <|.. WhatsAppClient
    WhatsAppClient --> WhatsAppConfig
    WhatsAppClient --> MessageResponse
```

## API Methods

### Text Messages
```python
send_text_message(to: str, message: str) -> MessageResponse
```

### Media Messages
```python
send_audio_message(to: str, file_path: str) -> MessageResponse
download_media(media_id: str, media_type: str, phone_number: str) -> str
```

### Templates
```python
send_template_message(to: str, template_name: str, language_code: str) -> MessageResponse
```

## Webhook Flow
```mermaid
sequenceDiagram
    participant WhatsApp
    participant Webhook
    participant Handler
    participant Storage

    WhatsApp->>Webhook: Send Message Event
    Webhook->>Handler: Process Notification
    Handler->>Storage: Save Media (if any)
    Handler->>WhatsApp: Send Response
    WhatsApp->>Handler: Delivery Status
