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
        args = record.args

        # Legacy Uvicorn access record:
        # (client_addr, method, path, http_version, status_code)
        if not args or len(args) < 3 or not isinstance(args[2], str):
            return True

        path = args[2].split("?", 1)[0]
        return not any(
            path == excluded or path.startswith(excluded + "/")
            for excluded in self.excluded_paths
        )


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIDFilter())
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


logging.getLogger("uvicorn.access").addFilter(EndpointAccessFilter(EXCLUDED_LOG_PATHS))
