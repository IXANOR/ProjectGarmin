from typing import AsyncGenerator, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.session_store import append_messages


router = APIRouter()


@router.post("/chat")
async def chat_endpoint(payload: dict) -> StreamingResponse:
    session_id = payload.get("session_id")
    messages: List[dict] | None = payload.get("messages")
    if not session_id or not isinstance(messages, list) or not messages:
        raise HTTPException(status_code=400, detail="Invalid request body")

    append_messages(session_id, messages)

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


