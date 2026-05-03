"""Manages chatbot session persistence and retrieval (in-memory, thread-safe)."""
import threading

_sessions = {}
_lock = threading.Lock()


def get_session(session_id):
    with _lock:
        return _sessions.get(session_id)


def save_session(session_id, data):
    with _lock:
        _sessions[session_id] = data


def clear_session(session_id):
    with _lock:
        _sessions.pop(session_id, None)
