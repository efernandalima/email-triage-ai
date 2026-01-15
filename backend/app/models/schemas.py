from pydantic import BaseModel
from typing import Literal

class AnalysisResult(BaseModel):
    category: Literal["Productive", "Improductive"]
    confidence: float
    summary: str
    suggested_response: str

class ErrorResponse(BaseModel):
    error: str
