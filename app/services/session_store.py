from typing import Dict, List, TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str


_SESSIONS: Dict[str, List[ChatMessage]] = {}


def append_messages(session_id: str, messages: List[ChatMessage]) -> None:
    history = _SESSIONS.setdefault(session_id, [])
    history.extend(messages)


def get_history(session_id: str) -> List[ChatMessage]:
    return list(_SESSIONS.get(session_id, []))


def clear_history(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)


