"""Application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Fraud Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
