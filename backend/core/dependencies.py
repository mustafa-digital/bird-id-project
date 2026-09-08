# backend/core/dependencies.py
import logging

from fastapi import File, HTTPException, Request, UploadFile

from backend.core.config import ALLOWED_CONTENT_TYPES, MAX_AUDIO_BYTES, settings

logger = logging.getLogger(__name__)


def get_model(request: Request):
    """Dependency to retrieve the model from the application state."""
    return request.app.state.model


def get_species_map_dict(request: Request):
    """Dependency to retrieve the species map dict from the application state."""
    return request.app.state.species_map_dict


def get_ffmpeg_path(request: Request):
    return request.app.state.ffmpeg_path


def get_settings():
    return settings


def validate_audio_upload(audio_file: UploadFile = File(...)) -> UploadFile:
    logger.info(f"Validating uploaded file: {audio_file.filename}")
    if audio_file.content_type not in ALLOWED_CONTENT_TYPES:
        logging.warning(
            f"File validation failed: unsupported content type: {audio_file.content_type}"
        )
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content type: {audio_file.content_type}",
        )
    if audio_file.size is not None and audio_file.size > MAX_AUDIO_BYTES:
        logger.warning(
            f"File validation failed: uploaded file is too large: {audio_file.size}"
        )
        raise HTTPException(
            status_code=413, detail="Uploaded file is too large, (10MB maximum)"
        )
    logger.info("Uploaded file passed initial validation.")
    return audio_file
