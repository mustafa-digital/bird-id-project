# backend/tests/test_model_loading.py
import pytest
from fastapi.testclient import TestClient
from backend.services.model_loader import load_model
from backend.core.config import DEVICE, WEIGHTS_PATH

def test_load_model_success():
    """Test that the model loads successfully with valid weights."""
    model = load_model(WEIGHTS_PATH, device=DEVICE)
    assert model is not None
    assert model.training is False

def test_load_model_missing_file():
    """Test that loading a model with a missing weights file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_model("non_existent_file.pth", device=DEVICE)





