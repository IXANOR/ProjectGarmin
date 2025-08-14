from fastapi import FastAPI


app = FastAPI(title="Garmin Backend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


