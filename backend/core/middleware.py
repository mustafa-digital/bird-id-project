# backend/core/middleware.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.request_context import request_id_var

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response