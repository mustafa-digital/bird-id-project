# config.py
import os
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

WEIGHTS_PATH = "backend/models/cnn14_model.pth"
SPECIES_MAP_PATHS = {
    "label_map": "backend/models/label_map.json",
    "species_ebird_map": "backend/models/species_to_ebird_map.json",
}
# FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-9.0.1-full_build-shared\bin\ffmpeg.exe"
DEVICE = "cpu"
MODEL_CONFIG = {
    "sample_rate": 32000,
    "window_size": 1024,
    "hop_size": 320,
    "mel_bins": 64,
    "fmin": 50,
    "fmax": 14000,
    "classes_num": 264,
}

CROP_LENGTH = 10  # seconds
PREDICTION_THRESHOLD = 0.05

MAX_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = [
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/mp4",
    "audio/aac",
    "audio/mp3",
]

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DB_DIR = "./backend/vector_store/chroma_db"
CHAT_MODEL = "openai/gpt-oss-20b"
MAX_QUERY_SIZE = 4000
TOP_K_DOCUMENTS = 10


class Settings(BaseSettings):
    ffmpeg_path: Path | None = None
    logging_level: str | None = "INFO"
    hf_token: SecretStr
    groq_api_key: SecretStr
    langsmith_tracing: bool
    langsmith_endpoint: str
    langsmith_api_key: SecretStr
    langsmith_project: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
os.environ["HF_TOKEN"] = settings.hf_token.get_secret_value()
os.environ["GROQ_API_KEY"] = settings.groq_api_key.get_secret_value()
