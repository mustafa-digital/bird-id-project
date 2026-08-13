# backend/core/dependencies.py
from fastapi import Request

def get_model(request: Request):
    """Dependency to retrieve the model from the application state."""
    return request.app.state.model

def get_species_map_dict(request: Request):
    """Dependency to retrieve the species map dict from the application state."""
    return request.app.state.species_map_dict

def get_ffmpeg_path(request: Request):
    return request.app.state.ffmpeg_path