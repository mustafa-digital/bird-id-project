# backend/core/lifespan.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import shutil
import logging
import subprocess

from backend.services.model_loader import load_model
from backend.utils.json import load_json
from backend.core.ffmpeg_config import setup_ffmpeg
from backend.core.config import WEIGHTS_PATH, SPECIES_MAP_PATHS, DEVICE

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Async context manager for application lifespan events.
     This method loads the model and other utility files on startup."""
    logger.info("Loading model...")
    try:
        app.state.model = load_model(WEIGHTS_PATH, DEVICE)
        logger.info("Model loaded successfully.")
    except (FileNotFoundError, RuntimeError) as e:
        logger.critical(f"Model failed to load, aborting startup: {e}")
        raise

    # FFmpeg setup
    logger.info("Setting up FFmpeg...")
    try:
        setup_ffmpeg(app)
    except RuntimeError as e:
        logger.critical(f"Could not resolve ffmpeg: {e}")
        raise

    # Load utility files
    logger.info("Loading utility files...")
    try: 
        app.state.species_map_dict = {
            "label_map": load_json(SPECIES_MAP_PATHS["label_map"]),
            "species_ebird_map": load_json(SPECIES_MAP_PATHS["species_ebird_map"]),
        }
        logger.info("Utility files loaded successfully.")
    except (FileNotFoundError, ValueError) as e:
        logger.critical(f"Utility files failed to load, aborting startup: {e}")
        raise

    yield

    logger.info("Application shutting down.")
    app.state.model = None
