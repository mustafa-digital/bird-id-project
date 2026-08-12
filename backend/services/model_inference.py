# backend.services.model_inference.py
import torch

def model_inference(model, waveform):
    with torch.no_grad():
        output = model(waveform)
    return output["clipwise_output"].squeeze(0)
