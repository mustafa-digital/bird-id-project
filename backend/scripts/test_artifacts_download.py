# backend/scripts/test_artifacts_download.py

import os
from pathlib import Path

import torch

from backend.core.artifacts import download_file, download_prefix
from backend.services.model_inference import model_inference
from backend.services.model_loader import load_model

BUCKET = os.environ["S3_BUCKET"]
out = Path("/tmp/artifact_test")

download_file(BUCKET, "models/cnn14_model.pth", out / "weights.pth")
download_prefix(BUCKET, "vector_store/chroma_db", out / "chroma_db")
download_prefix(BUCKET, "vector_store/embedding_model", out / "embedding_model")

print((out / "weights.pth").stat().st_size)
print(sorted(p.name for p in (out / "chroma_db").iterdir()))
print(sorted(p.name for p in (out / "embedding_model").iterdir()))

model = load_model(Path("/tmp/artifact_test/weights.pth"))
dummy_tensor = torch.randn(1, 320000)

output = model_inference(model, dummy_tensor)
print(output.shape)
