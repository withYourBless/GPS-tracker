from pydantic import BaseModel

from typing import Optional

from src.endpoints.models.trackFilteredResponse import TrackFilteredResponse
from src.endpoints.models.userResponse import UserResponse


class InfoResponse(BaseModel):
    user: Optional[UserResponse] = None
    tracks: Optional[TrackFilteredResponse] = None
