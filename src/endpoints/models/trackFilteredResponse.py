from pydantic import BaseModel

from src.endpoints.models.trackResponse import TrackResponse
from typing import List, Optional


class TrackFilteredResponse(BaseModel):
    tracks: Optional[List[TrackResponse]] = None
