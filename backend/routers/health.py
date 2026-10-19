# backend/routers/health.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", include_in_schema=False)
def health(request: Request):
    state = request.app.state
    checks = {
        "audio_model": getattr(state, "model", None) is not None,
        "vector_store_retriever": getattr(state, "retriever", None) is not None,
    }
    if not all(checks.values()):
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "checks": checks}
        )
    return {"status": "ok", "checks": checks}
