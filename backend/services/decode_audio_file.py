# backend/services/decode_audio_file.py
from fastapi import UploadFile
import asyncio
import tempfile
from pathlib import Path
import soundfile as sf
import torch
import numpy as np
import subprocess
import logging

from backend.core.exceptions import (
    AudioReadError, UnsupportedAudioError, EmptyAudioError,
    DecoderUnavailableError, AudioDecodingTimeOutError, AudioUploadSizeError
)

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 10 * 1024 * 1024 # 10MB file limit

async def decode_audio_file(file: UploadFile, 
                            target_sr: int, 
                            ffmpeg_path: Path):

    # Extract extension from file if it has one, else append with ".audio"
    filename = file.filename or "input.audio"
    suffix = Path(filename).suffix.lower() or ".audio"

    logger.info(f"Reading uploaded audio file...")
    try:
        source_data = await file.read()
    except Exception as e:
        error_msg = f"Failed to read audio file: {e}"
        logger.warning(error_msg)
        raise AudioReadError(error_msg)

    if not source_data:
        error_msg = f"Uploaded audio file is empty."
        logger.error(error_msg)
        raise EmptyAudioError(error_msg)
    
    if len(source_data) > MAX_AUDIO_BYTES:
        error_msg = f"Uploaded file size exceeds maximum size of {MAX_AUDIO_BYTES}"
        logger.error(error_msg)
        raise AudioUploadSizeError(error_msg)

    logger.info("Uploaded file read successfully.")
    logger.info(f"Read {len(source_data)} bytes from uploaded file: {filename}")
    
    # Write the inputfile to a temp file to decode it using ffmpeg, 
    # then read the decoded audio using soundfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        source_path = temp_dir / f"input{suffix}"
        wav_path = temp_dir / "output.wav"

        logger.info("Writing to temporary file...")
        source_path.write_bytes(source_data)

        command = [
            str(ffmpeg_path),
            "-hide_banner",
            "-loglevel",
            "info",
            "-y",
            "-i",
            str(source_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            f"{target_sr}",
            "-c:a",
            "pcm_s16le",
            "-f",
            "wav",
            "-t", 
            "10",
            str(wav_path),
        ]

        logger.info("Running ffmpeg to decode audio...")
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired:
            error_msg = "FFmpeg audio decoding timed out"
            raise AudioDecodingTimeOutError(error_msg)
        except Exception as exc:
            error_msg = (f"Could not launch FFmpeg: {type(exc).__name__}, "
            f"PATH: {str(ffmpeg_path)}"
            )
            logger.exception(error_msg)
            raise DecoderUnavailableError(error_msg)

        # FFmpeg process completed but unsuccessful
        if result.returncode != 0:
            stderr_text = result.stderr.decode(errors="replace")
            logger.error(f"FFmpeg failed (exit {result.returncode}): {stderr_text}")
            error_msg = f"FFmpeg failed internally"
            raise UnsupportedAudioError(error_msg)

        # FFmpeg did not produce a valid wav file
        if not wav_path.is_file() or wav_path.stat().st_size == 0:
            logger.error(
                f"FFmpeg success (exit 0) but produced invalid output"
                f"stdout: {result.stdout.decode(errors='replace')}"
            )
            raise UnsupportedAudioError(
                "Audio could not be processed - the file may contain invalid audio" \
                "or use an unsupported format."
            )

        logger.info("FFmpeg successfully decoded input audio into wav format.")
        logger.info("Transforming wav file into a torch tensor...")
        # Use soundfile to decode the wav file
        try:
            samples, sr = sf.read(
                wav_path,
                dtype="float32",
                always_2d=True,
            )
        except Exception as e:
            logger.error(f"Soundfile could not decode wav file: {e}")
            raise UnsupportedAudioError(f"Error decoding audio: {e}")

        if samples.size == 0:
            raise UnsupportedAudioError("Decoded audio contains no samples.")

        if not np.isfinite(samples).all():
            raise UnsupportedAudioError("Decoded audio contains invalid (NaN/Inf) values.")
            
    waveform = torch.from_numpy(samples.T) # Convert to a torch tensor
    return waveform, sr
    