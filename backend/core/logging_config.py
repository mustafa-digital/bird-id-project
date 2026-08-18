# backend/core/logging_config.py
import logging
from pythonjsonlogger import jsonlogger
import sys
from backend.core.request_context import get_request_id

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIDFilter())
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s | %(request_id)s | %(name)s | %(levelname)s | %(message)s",
        json_indent=4,
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv = logging.getLogger(name)
        uv.handlers = [handler]
        uv.propagate = False