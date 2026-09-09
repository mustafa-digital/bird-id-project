# backend/tests/conftest.py
import io
import logging

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from backend.core.dependencies import get_model
from backend.main import app
from backend.services import model_inference

# Set the root logger to CRITICAL to suppress almost all logs
root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)

# Disable all handlers on the root logger
for handler in root_logger.handlers[:]:
    handler.setLevel(logging.CRITICAL)
    handler.filter = lambda record: False  # drop all records

# Explicitly silence known noisy loggers
for name in [
    "root",
    "backend",
    "backend.services",
    "backend.services.decode_audio_file",
    "httpx",
    "httpcore",
    "asyncio",
    "numba",
    "numba.core",
]:
    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL)
    logger.handlers.clear()
    logger.propagate = False


class MockModel:
    def __call__(self, waveform) -> {}:
        import torch

        batch_size = waveform.shape[0]
        return {
            "clipwise_output": torch.rand(batch_size, 264),
            "framewise_output": torch.rand(batch_size, 101, 264),
        }

    def eval(self):
        return self


def get_mock_model():
    return MockModel()


@pytest.fixture(scope="session")
def client_with_mock_prediction():

    from unittest.mock import patch

    import torch

    async def mock_prediction_fixture(data):
        return torch.rand(264)

    with patch("backend.core.lifespan.load_model", return_value=MockModel()):
        with TestClient(app, raise_server_exceptions=True) as client:
            app.dependency_overrides[model_inference] = mock_prediction_fixture
            app.dependency_overrides[get_model] = get_mock_model
            yield client

            app.dependency_overrides.clear()


@pytest.fixture
def valid_wav_bytes() -> io.BytesIO:
    samples = np.random.uniform(-0.5, 0.5, 32000 * 3).astype(
        "float32"
    )  # 3 seconds of random noise
    buf = io.BytesIO()
    sf.write(buf, samples, samplerate=32000, format="WAV")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def unsupported_file_type() -> io.BytesIO:
    data = b"Fake binary content for unsupported file type test."
    buf = io.BytesIO(data)
    buf.seek(0)
    return buf.read()


@pytest.fixture
def empty_audio_bytes() -> io.BytesIO:
    return b""


@pytest.fixture
def corrupt_audio_bytes() -> io.BytesIO:
    return b"Simulation of corrupt audio data"
