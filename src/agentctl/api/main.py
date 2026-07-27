from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI(title="agentctl", version="0.1.0")
app.mount("/metrics", make_asgi_app())


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    # Production implementation should check provider, index, and database.
    return {"status": "ready"}
