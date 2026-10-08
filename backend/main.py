# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import CORS_ORIGINS
from backend.core.lifespan import lifespan
from backend.core.logging_config import setup_logging
from backend.core.middleware import RequestIDMiddleware
from backend.routers import chat, predictions

# Configure Logging
setup_logging()

# Initialize FastAPI app, load model and utility files on startup with lifespan
app = FastAPI(
    title="Bird Species Audio Classifier",
    description="API for classifying bird species from audio recordings",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.include_router(predictions.router)
app.include_router(chat.router)


# REMOVE LATER
@app.get("/")
async def root():
    return {"message": "Welcome to the Bird Species Audio Classifier API!"}
