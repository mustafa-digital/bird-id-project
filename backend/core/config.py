# config.py

WEIGHTS_PATH = "backend/models/cnn14_model.pth"
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


