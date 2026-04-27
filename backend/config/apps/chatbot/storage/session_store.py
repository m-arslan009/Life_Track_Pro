from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def _get_session_model():
    from config.apps.chatbot.models import ChatSession
    return ChatSession


@dataclass
class SessionData:
    user_id: int
    session_id: str
    pending_command: dict | None = None
    missing_fields: list[str] = field(default_factory=list)
    context_data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class SessionStore:
    def get(self, session_id: str) -> SessionData | None:
        ChatSession = _get_session_model()
        try:
            session = ChatSession.objects.select_related("user").get(session_id=session_id)
            return SessionData(
                user_id=session.user_id,
                session_id=session.session_id,
                pending_command=session.pending_command,
                missing_fields=session.missing_fields or [],
                context_data=session.context_data or {},
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
        except ChatSession.DoesNotExist:
            return None

    def create(self, session_id: str, user_id: int) -> SessionData:
        ChatSession = _get_session_model()
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            user_id=user_id,
        )
        return SessionData(
            user_id=session.user_id,
            session_id=session.session_id,
            pending_command=session.pending_command,
            missing_fields=session.missing_fields or [],
            context_data=session.context_data or {},
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def update(self, session_id: str, **kwargs) -> SessionData | None:
        ChatSession = _get_session_model()
        try:
            session = ChatSession.objects.get(session_id=session_id)
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.save()
            return self.get(session_id)
        except ChatSession.DoesNotExist:
            return None

    def clear_pending(self, session_id: str) -> None:
        ChatSession = _get_session_model()
        ChatSession.objects.filter(session_id=session_id).update(
            pending_command=None,
            missing_fields=[],
        )

    def delete(self, session_id: str) -> None:
        ChatSession = _get_session_model()
        ChatSession.objects.filter(session_id=session_id).delete()