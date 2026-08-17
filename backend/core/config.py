# config.py
from pydantic_settings import BaseSettings

WEIGHTS_PATH = "backend/models/cnn14_model.pth"
SPECIES_MAP_PATHS = {
    "label_map": "backend/models/label_map.json",
    "species_ebird_map" : "backend/models/species_to_ebird_map.json",
}
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-9.0.1-full_build-shared\bin\ffmpeg.exe"
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

CROP_LENGTH = 10 # seconds
PREDICTION_THRESHOLD = 0.05

class Settings(BaseSettings):
    ffmpeg_path: str | None = None
    weights_path: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()


