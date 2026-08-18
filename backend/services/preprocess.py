# backend/services/preprocess.py
from fastapi import UploadFile
from pathlib import Path
import torch
import logging

from backend.services.decode_audio_file import decode_audio_file

logger = logging.getLogger(__name__)

async def preprocess_audio(audio_file: UploadFile,
                           ffmpeg_path: Path, 
                           target_sr: int = 32000, 
                           crop_samples: int = 320000) -> torch.Tensor:
    """Preprocess audio bytes for model input.
    Args:
        audio_bytes (bytes): The raw audio bytes.
        target_sr (int): The target sample rate for the audio.
        crop_samples (int): The number of samples to crop or pad the audio to.
        Returns:
            torch.Tensor: The preprocessed audio tensor.
    """
    waveform, _ = await decode_audio_file(audio_file, target_sr, ffmpeg_path)
    logger.info(f"Audio file decoded successfully.")
    logger.info(f"Processing waveform...")

    waveform = waveform.squeeze(0)  # Remove channel dimension

    # Crop or pad the waveform to the desired length
    length = waveform.shape[0]
    if length < crop_samples:
        # Pad with zeros if the waveform is shorter than the desired length
        waveform = torch.nn.functional.pad(waveform, (0, crop_samples - length))
    else:
        start = (length - crop_samples) // 2
        waveform = waveform[start:start + crop_samples]
    return waveform.unsqueeze(0)  # Return waveform with a batch dimension
