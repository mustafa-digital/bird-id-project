# main.py
from fastapi import FastAPI
from backend.core.logging_config import setup_logging
from backend.core.lifespan import lifespan
from backend.routers import predictions

# Configure Logging
setup_logging()

"""from pathlib import Path
import os

conda_root = Path(os.environ["CONDA_PREFIX"])
for sub in [r"Library\bin", r"Library\mingw-w64\bin"]:
    p = conda_root / sub
    if p.exists():
        os.add_dll_directory(str(p))
"""
# Initialize FastAPI app, load model and utility files on startup with lifespan
app = FastAPI(
    title="Bird Species Audio Classifier",
    description="API for classifying bird species from audio recordings",
    lifespan=lifespan
)

app.include_router(predictions.router)

# REMOVE LATER
@app.get("/")
async def root():
    return {"message": "Welcome to the Bird Species Audio Classifier API!"}
