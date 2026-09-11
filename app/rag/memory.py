class ConversationMemory:
    """Store recent conversation history."""

    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        """Add a message to conversation history."""
        self.history.append({
            "role": role,
            "content": content
        })

    def get_history(self):
        """Return complete conversation history."""
        return self.history

    def clear(self):
        """Clear conversation history."""
        self.history = []