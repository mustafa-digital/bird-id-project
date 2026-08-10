# main.py

from fastapi import FastAPI
from backend.core.logging_config import setup_logging
from backend.core.lifespan import lifespan

# Configure Logging
setup_logging()

# Initialize FastAPI app, load model on startup with lifespan
app = FastAPI(lifespan=lifespan)

    



