from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.api.settings import router as settings_router
from app.api.files import router as files_router
from app.api.images import router as images_router
from app.api.audio import router as audio_router
from app.api.system import router as system_router
from app.api.context import router as context_router
from app.api.personality import router as personality_router
from app.api.theme import router as theme_router
from app.core.db import init_db


app = FastAPI(title="Garmin Backend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


init_db()
app.include_router(chat_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(images_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(context_router, prefix="/api")
app.include_router(personality_router, prefix="/api")
app.include_router(theme_router, prefix="/api")

