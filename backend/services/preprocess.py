# backend/services/preprocess.py
import torch
import torchaudio as ta
import soundfile as sf
import io


def preprocess_audio(audio_bytes: bytes, target_sr: int = 32000, crop_samples: int = 320000) -> torch.Tensor:
    """Preprocess audio bytes for model input.
    Args:
        audio_bytes (bytes): The raw audio bytes.
        target_sr (int): The target sample rate for the audio.
        crop_samples (int): The number of samples to crop or pad the audio to.
        Returns:
            torch.Tensor: The preprocessed audio tensor.
    """
    try:
        waveform, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
    except Exception as e:
        raise ValueError(f"Could not decode audio: {e}")

    # Model excepts single channel audio, so average channels if more than one
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)

    # Resample if the sample rate is different from the target sample rate
    """
    if sr != target_sr:
        waveform = ta.functional.resample(waveform, sr, target_sr)
    """
    if sr != target_sr:
        waveform_tensor = torch.from_numpy(waveform)
        waveform_tensor = ta.functional.resample(waveform_tensor, sr, target_sr)
        waveform = waveform_tensor

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
