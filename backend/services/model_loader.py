from backend.models.panns.panns_models import Cnn14_DecisionLevelAtt
from backend.core.config import MODEL_CONFIG

import torch
import os

def load_model(weights_path: str, device: str ="cpu"):
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
    if not os.path.exists(weights_path):
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