from pydantic import BaseModel

from typing import Optional, List

from src.service.models.trackOut import TrackOut
from src.service.models.userOut import UserOut


class InfoOut(BaseModel):
    user: Optional[UserOut] = None
    tracks: Optional[List[TrackOut]] = None
