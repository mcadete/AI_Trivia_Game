from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ChatMemory:
    def __init__(self, max_messages: int = 50):
        self.messages: List[ChatMessage] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the chat history"""
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
        
        # Trim history if it exceeds max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_history(self, last_n: Optional[int] = None) -> List[Dict]:
        """Get chat history, optionally limited to last n messages"""
        messages = self.messages[-last_n:] if last_n else self.messages
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def clear_history(self) -> None:
        """Clear all chat history"""
        self.messages = []
    
    def get_context_window(self, window_size: int = 5) -> str:
        """Get the last n messages as a formatted string for context"""
        recent_messages = self.messages[-window_size:]
        context = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in recent_messages
        ])
        return context
    
    def to_openai_messages(self) -> List[Dict[str, str]]:
        """Convert chat history to OpenAI message format"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ] 