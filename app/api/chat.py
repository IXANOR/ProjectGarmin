from typing import AsyncGenerator, List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from sqlmodel import Session

from app.core.db import get_session
from app.models.session import SessionModel, MessageModel


router = APIRouter()


@router.post("/chat")
async def chat_endpoint(payload: dict, db: Session = Depends(get_session)) -> StreamingResponse:
    session_id = payload.get("session_id")
    messages: List[dict] | None = payload.get("messages")
    if not session_id or not isinstance(messages, list) or not messages:
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Ensure session exists
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Persist incoming user messages
    for msg in messages:
        db.add(MessageModel(session_id=session_id, role=msg.get("role", "user"), content=msg.get("content", "")))
    # Persist assistant reply (mock)
    assistant_full = "Hello from mock AI!"
    db.add(MessageModel(session_id=session_id, role="assistant", content=assistant_full))
    db.commit()

    async def event_stream() -> AsyncGenerator[bytes, None]:
        tokens = ["Hello", "from", "mock", "AI!"]
        for token in tokens:
            yield f"data: {token}\n\n".encode()
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


