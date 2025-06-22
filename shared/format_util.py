def format_user_messages_with_index(messages):
    return "\n".join(f"{idx + 1}. {msg}" for idx, msg in enumerate(messages))
