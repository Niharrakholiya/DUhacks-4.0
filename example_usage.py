from app.message_store import MessageStore

# Initialize the store
store = MessageStore()

# Example: Store a text message
store.store_message(
    phone_number="919574156941",
    message_type="text",
    content="I have a headache",
    response="Let me ask you some questions about your headache..."
)

# Example: Store a voice note
store.store_message(
    phone_number="919574156941",
    message_type="audio",
    file_path="media/919574156941_20250223165453.m4a",
    response="I understand you're experiencing..."
)

# Get user history
history = store.get_user_history("919574156941")
print("User history:", history)

# Get last message
last_msg = store.get_last_message("919574156941")
print("Last message:", last_msg)
