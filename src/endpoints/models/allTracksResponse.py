from typing import Optional, List

from pydantic import BaseModel

from src.endpoints.models.trackResponse import TrackResponse


class AllTracksResponse(BaseModel):
    tracks: Optional[List[TrackResponse]] = None
