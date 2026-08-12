# backend/routers/predictions.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
import numpy as np
import logging

from backend.core.dependencies import get_model, get_species_map_dict
from backend.services.preprocess import preprocess_audio
from backend.services.model_inference import model_inference
from backend.core.config import MODEL_CONFIG, CROP_LENGTH, PREDICTION_THRESHOLD

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict")
async def predict(audio_file: UploadFile = File(...), model=Depends(get_model), species_map_dict=Depends(get_species_map_dict)):
    # Read uploaded audio file
    audio_bytes = await audio_file.read()

    sample_rate = MODEL_CONFIG["sample_rate"] # default 32000
    crop_samples = sample_rate * CROP_LENGTH # default 32000 * 10
    try:
        waveform = preprocess_audio(audio_bytes, target_sr=sample_rate, crop_samples=crop_samples)
    except ValueError as e:
        logger.error(f"Audio preprocessing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Model inference
    probs = await run_in_threadpool(model_inference, model, waveform)
    logger.info(f"Model inference completed successfully.")

    probs_np = probs.numpy()
    predicted_indices = np.where(probs_np >= PREDICTION_THRESHOLD)[0]
    predicted_indices = predicted_indices[np.argsort(-probs_np[predicted_indices])]  # Sort by confidence
    logger.info(f"Predicted indices above threshold: {predicted_indices}")
    label_map = species_map_dict["label_map"]
    species_to_ebirdcode = species_map_dict["species_ebird_map"]
    idx_to_ebirdcode = {v: k for k, v in label_map.items()}
    ebirdcode_to_species = {v: k for k, v in species_to_ebirdcode.items()}

    predictions = [
        {"species_name": ebirdcode_to_species[idx_to_ebirdcode[i]],
         "species_code": idx_to_ebirdcode[i], 
         "confidence": float(probs_np[i])}
        for i in predicted_indices
    ]
    return predictions

