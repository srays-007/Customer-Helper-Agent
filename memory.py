from datetime import datetime


class ConversationMemory:
    """Simple in-memory conversation history for the current server session."""

    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages

    def add(self, role, content):
        self.messages.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat(timespec="seconds")
        })

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self):
        if not self.messages:
            return "No previous conversation."

        lines = []
        for message in self.messages[-6:]:
            role = message["role"].capitalize()
            lines.append(f"{role}: {message['content']}")

        return "\n".join(lines)

    def clear(self):
        self.messages.clear()
