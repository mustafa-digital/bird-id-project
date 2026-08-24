# backend/routers/predictions.py
import logging

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from backend.core.config import CROP_LENGTH, MODEL_CONFIG, PREDICTION_THRESHOLD
from backend.core.dependencies import (
    get_ffmpeg_path,
    get_model,
    get_species_map_dict,
    validate_audio_upload,
)
from backend.core.exceptions import (
    AudioDecodingTimeOutError,
    AudioReadError,
    AudioUploadSizeError,
    DecoderUnavailableError,
    EmptyAudioError,
    UnsupportedAudioError,
)
from backend.core.request_context import get_request_id
from backend.schemas.prediction import PredictionResponse
from backend.services.model_inference import model_inference
from backend.services.preprocess import preprocess_audio

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    audio_file: UploadFile = Depends(validate_audio_upload),
    model=Depends(get_model),
    species_map_dict=Depends(get_species_map_dict),
    ffmpeg_path=Depends(get_ffmpeg_path),
    request_id=Depends(get_request_id),
) -> PredictionResponse:

    sample_rate = MODEL_CONFIG["sample_rate"]  # default 32000
    crop_samples = sample_rate * CROP_LENGTH  # default 32000 * 10
    try:
        waveform = await preprocess_audio(
            audio_file,
            ffmpeg_path=ffmpeg_path,
            target_sr=sample_rate,
            crop_samples=crop_samples,
        )
    except (EmptyAudioError, AudioUploadSizeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (UnsupportedAudioError, AudioReadError) as e:
        raise HTTPException(status_code=415, detail=str(e))
    except AudioDecodingTimeOutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except DecoderUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    logger.info("Audio processing completed.")
    logger.info("Running model inference...")

    # Model inference
    probs = await run_in_threadpool(model_inference, model, waveform)
    logger.info("Model inference completed successfully.")

    probs_np = probs.numpy()
    predicted_indices = np.where(probs_np >= PREDICTION_THRESHOLD)[0]
    # Sort by confidence
    predicted_indices = predicted_indices[np.argsort(-probs_np[predicted_indices])]
    logger.info(f"Predicted indices above threshold: {predicted_indices}")

    label_map = species_map_dict["label_map"]
    species_to_ebirdcode = species_map_dict["species_ebird_map"]
    idx_to_ebirdcode = {v: k for k, v in label_map.items()}
    ebirdcode_to_species = {v: k for k, v in species_to_ebirdcode.items()}

    predictions = [
        {
            "species_name": ebirdcode_to_species[idx_to_ebirdcode[i]],
            "species_code": idx_to_ebirdcode[i],
            "confidence": float(probs_np[i]),
        }
        for i in predicted_indices
    ]

    logger.info("Predictions OK. Sending response.")
    return PredictionResponse(
        request_id=request_id,
        confidence_threshold=PREDICTION_THRESHOLD,
        predictions=predictions,
    )
