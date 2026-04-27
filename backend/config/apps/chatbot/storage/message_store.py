from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def _get_models():
    from config.apps.chatbot.models import ChatMessage, ChatSession
    return ChatMessage, ChatSession


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class MessageStore:
    def add(self, session_id: str, role: str, content: str, user_id: int | None = None, metadata: dict | None = None) -> Message:
        ChatMessage, ChatSession = _get_models()
        
        # Ensure session exists before adding message
        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            if user_id is None:
                raise ValueError(f"Cannot create message: no session exists and no user_id provided")
            session, _ = ChatSession.objects.get_or_create(
                session_id=session_id,
                user_id=user_id,
            )
        
        message = ChatMessage.objects.create(
            session=session,
            role=role,
            content=content,
            metadata=metadata or {},
        )
        return Message(
            role=message.role,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.metadata,
        )

    def get_history(self, session_id: str, limit: int | None = None) -> list[Message]:
        ChatMessage, ChatSession = _get_models()
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = ChatMessage.objects.filter(session=session).order_by("timestamp")
            if limit:
                messages = messages[:limit]
            return [
                Message(role=m.role, content=m.content, timestamp=m.timestamp, metadata=m.metadata)
                for m in messages
            ]
        except ChatSession.DoesNotExist:
            return []

    def clear(self, session_id: str) -> None:
        ChatMessage, _ = _get_models()
        ChatMessage.objects.filter(session__session_id=session_id).delete()