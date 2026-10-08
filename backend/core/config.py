# config.py
import os
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

SPECIES_MAP_PATHS = {
    "label_map": BASE_DIR / "models" / "label_map.json",
    "species_ebird_map": BASE_DIR / "models" / "species_to_ebird_map.json",
}

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
PREDICTION_THRESHOLD = 0.10

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
CHAT_MODEL = "openai/gpt-oss-20b"
MAX_QUERY_SIZE = 4000
TOP_K_DOCUMENTS = 10


class Settings(BaseSettings):
    ffmpeg_path: Path
    weights_path: Path
    chroma_db_dir: Path
    logging_level: str | None = "INFO"
    hf_token: SecretStr
    groq_api_key: SecretStr
    langsmith_tracing: bool
    langsmith_endpoint: str
    langsmith_api_key: SecretStr
    langsmith_project: str
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
# Some libraries require api keys to be set using os.environ.
os.environ["HF_TOKEN"] = settings.hf_token.get_secret_value()
os.environ["GROQ_API_KEY"] = settings.groq_api_key.get_secret_value()
FFMPEG_PATH = settings.ffmpeg_path
WEIGHTS_PATH = settings.weights_path
CHROMA_DB_DIR = settings.chroma_db_dir

# Resolve cors origins if there are multiple separated by commas
CORS_ORIGINS = [
    origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
]
