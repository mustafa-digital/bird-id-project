# backend/core/lifespan.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from backend.services.model_loader import load_model
from backend.core.config import WEIGHTS_PATH, DEVICE

logger = logging.getLogger(__name__)
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Async context manager for application lifespan events.
     This method loads the model on startup."""
    logger.info("Logging model...")
    try:
        app_state["model"] = load_model(WEIGHTS_PATH, DEVICE)
        logger.info("Model loaded successfully.")
    except (FileNotFoundError, RuntimeError) as e:
        logger.critical(f"Model failed to load, aborting startup: {e}")
        raise
    
    yield

    logger.info("App shutting down.")
    app_state.clear()
