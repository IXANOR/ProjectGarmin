from fastapi import FastAPI
from app.api.chat import router as chat_router


app = FastAPI(title="Garmin Backend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(chat_router, prefix="/api")

