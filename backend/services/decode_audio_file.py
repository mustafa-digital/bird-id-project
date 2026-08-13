# backend/services/decode_audio_file.py
from fastapi import UploadFile, HTTPException
import asyncio
import tempfile
from pathlib import Path
import soundfile as sf
import torch
import subprocess
import logging

logger = logging.getLogger(__name__)

#
#ffmpeg_path = Path(FFMPEG_PATH)

async def decode_audio_file(file: UploadFile, 
                            target_sr: int, 
                            ffmpeg_path_str: str):
    
    ffmpeg_path = Path(ffmpeg_path_str)
    if not ffmpeg_path.is_file():
        raise RuntimeError(
            f"FFmpeg executable was not found: {ffmpeg_path}"
        )

    logger.info(f"Using FFmpeg: {ffmpeg_path}") 

    # Extract extension from file if it has one, else append with ".audio"
    filename = file.filename or "input.audio"
    suffix = Path(filename).suffix.lower() or ".audio"

    source_data = await file.read()
    logger.info(f"Received {len(source_data)} bytes")

    if not source_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded audio file is empty."
        )
    
    # Write the inputfile to a temp file to decode it using ffmpeg, 
    # then read the decoded audio using soundfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        source_path = temp_dir / f"input{suffix}"
        wav_path = temp_dir / "output.wav"

        source_path.write_bytes(source_data)

        command = [
            ffmpeg_path_str,
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
            str(wav_path),
        ]

        try:
            await asyncio.to_thread(
                subprocess.run,
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(
                status_code=504,
                detail="FFmpeg audio decoding timed out",
            ) from exc
        except Exception as exc:
            logger.exception("Could not launch FFmpeg")
            raise HTTPException(
                status_code=500,
                detail=f"Could not launch FFmpeg: {type(exc).__name__}",
            ) from exc

        if not wav_path.is_file():
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg completed but did not produce WAV output"
            )

        # Use soundfile to decode the wav file
        samples, sr = sf.read(
            wav_path,
            dtype="float32",
            always_2d=True,
        )
    
    waveform = torch.from_numpy(samples.T) # Convert to a torch tensor
    return waveform, sr
    