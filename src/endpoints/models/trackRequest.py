from datetime import datetime

from pydantic import BaseModel, StrictStr


class TrackRequest(BaseModel):
    user_id: StrictStr
    latitude: StrictStr
    longitude: StrictStr
    timestamp: datetime
