# backend/core/ffmpeg_config.py
from fastapi import FastAPI
from pathlib import Path
import subprocess
import shutil
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

def resolve_ffmpeg_path(configured: Path | None) -> Path:
    if configured:
        return configured
    logger.info("FFmpeg path not configured in config, checking system PATH.")
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg not found in PATH or configured in settings")
    return Path(path)

def validate_ffmpeg(path: Path) -> None:
    path_str = str(path)
    try:
        result = subprocess.run(
            [path_str, "-version"],
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