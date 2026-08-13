# backend/core/ffmpeg_config.py
from fastapi import FastAPI
import subprocess
import shutil

from backend.core.config import settings

def resolve_ffmpeg_path(configured: str | None) -> str:
    if configured:
        return configured
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg not found in PATH or configured in settings")
    return path

def validate_ffmpeg(path: str) -> None:
    try:
        result = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
    except FileNotFoundError as e:
        raise RuntimeError(f"ffmpeg binary not found at {path}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg at {path} failed to run: {e.stderr.strip()}") from e
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffmpeg at {path} did not respond in time")

def setup_ffmpeg(app: FastAPI) -> None:
    path = resolve_ffmpeg_path(settings.ffmpeg_path)
    validate_ffmpeg(path)
    app.state.ffmpeg_path = path