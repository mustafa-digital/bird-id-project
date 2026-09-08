# backend/schemas/prediction.py

from pydantic import BaseModel, Field


class SpeciesPrediction(BaseModel):
    species_name: str = Field(description="The name of the species.")
    species_code: str = Field(description="The ebird code of this species.")
    confidence: float = Field(
        ge=0.0, le=1.0, description="The model's confidence score for this species."
    )


class PredictionResponse(BaseModel):
    request_id: str
    confidence_threshold: float
    predictions: list[SpeciesPrediction]
