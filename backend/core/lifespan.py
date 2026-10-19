# backend/core/lifespan.py
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core import rag_config
from backend.core.artifacts import ArtifactDownloadError, download_file, download_prefix
from backend.core.config import (
    CHROMA_DB_DIR,
    DEVICE,
    EMBEDDING_MODEL_DIR,
    EMBEDDING_MODEL_S3_PREFIX,
    KB_S3_PREFIX,
    MODEL_S3_KEY,
    S3_BUCKET,
    SPECIES_MAP_PATHS,
    WEIGHTS_PATH,
)
from backend.core.ffmpeg_config import setup_ffmpeg
from backend.services.model_loader import load_embedding_model, load_model
from backend.utils.json_utils import load_json

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application lifespan events.
    This method loads the model and other utility files on startup."""

    logger.info("Loading models and artifacts...")
    try:
        await asyncio.to_thread(download_file, S3_BUCKET, MODEL_S3_KEY, WEIGHTS_PATH)
        await asyncio.to_thread(download_prefix, S3_BUCKET, KB_S3_PREFIX, CHROMA_DB_DIR)
        await asyncio.to_thread(
            download_prefix, S3_BUCKET, EMBEDDING_MODEL_S3_PREFIX, EMBEDDING_MODEL_DIR
        )
        app.state.model = load_model(WEIGHTS_PATH, DEVICE)
        app.state.embedding_model = load_embedding_model(EMBEDDING_MODEL_DIR)
        logger.info("Models and artifacts loaded successfully.")
    except (ArtifactDownloadError, FileNotFoundError, RuntimeError) as e:
        logger.critical(f"Model failed to load, aborting startup: {e}")
        raise

    # Initialize RAG components
    logger.info("Initializing RAG components...")
    try:
        app.state.retriever = rag_config.init_rag_service()
        app.state.chat_model = rag_config.init_chat_model()
        app.state.chat_prompt_template = rag_config.init_chat_prompt_template()
    except RuntimeError as e:
        logger.critical(e)
        raise
    logger.info("Successfully initialized RAG components.")

    # FFmpeg setup
    logger.info("Setting up FFmpeg...")
    try:
        setup_ffmpeg(app)
    except RuntimeError as e:
        logger.critical(f"Could not resolve ffmpeg: {e}")
        raise
    logger.info(f"FFmpeg loaded successfully. Path: {app.state.ffmpeg_path}")

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
