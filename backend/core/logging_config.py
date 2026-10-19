# backend/core/logging_config.py
import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from backend.core.request_context import get_request_id

EXCLUDED_LOG_PATHS = ["/health"]


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        record.request_id = get_request_id()
        return True


class EndpointAccessFilter(logging.Filter):
    def __init__(self, excluded_paths: set[str]):
        super().__init__()
        self.excluded_paths = excluded_paths

    def filter(self, record: logging.LogRecord):
        path = record.args[2] if record.args and len(record.args) >= 3 else ""
        return not any(
            path == p or path.startswith(p + "/") for p in self.excluded_paths
        )


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIDFilter())
    handler.addFilter(EndpointAccessFilter(excluded_paths=EXCLUDED_LOG_PATHS))
    formatter = JsonFormatter(
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
