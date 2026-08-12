# config.py

WEIGHTS_PATH = "backend/models/cnn14_model.pth"
SPECIES_MAP_PATHS = {
    "label_map": "backend/models/label_map.json",
    "species_ebird_map" : "backend/models/species_to_ebird_map.json",
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

CROP_LENGTH = 10 # seconds
PREDICTION_THRESHOLD = 0.1


