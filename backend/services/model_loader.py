from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer

from backend.core.config import DEVICE, MODEL_CONFIG
from backend.models.panns.panns_models import Cnn14_DecisionLevelAtt


def load_model(weights_path: Path, device: str = "cpu"):
    """Load the pre-trained model from the specified weights path.
    Args:
        weights_path (str): Path to the model weights file.
        device (str): Device to load the model on.
    Returns:
        torch.nn.Module: The loaded model.
    Raises:
        FileNotFoundError: If the weights file does not exist.
        RuntimeError: If the model fails to load due to architecture mismatch or other issues.
    """
    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found at {weights_path}")

    device = torch.device(device)
    # Load model
    model = Cnn14_DecisionLevelAtt(**MODEL_CONFIG)

    # Load weights
    try:
        state_dict = torch.load(weights_path, map_location=device, weights_only=True)
    except Exception as e:
        raise RuntimeError(f"Failed to load model weights from {weights_path}: {e}")
    try:
        model.load_state_dict(state_dict)
    except Exception as e:
        raise RuntimeError(f"State dict does not match model architecture: {e}")

    model.eval()
    model = model.to(device)
    return model


def load_embedding_model(embedding_model_dir: Path):
    if not embedding_model_dir.exists():
        raise FileNotFoundError(f"Embedding model not found at {embedding_model_dir}")

    try:
        model = SentenceTransformer(
            str(embedding_model_dir), local_files_only=True, device=DEVICE
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to load embedding model from {embedding_model_dir}: {e}"
        )

    return model
