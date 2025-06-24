from datetime import datetime

from pydantic import BaseModel, StrictStr


class TrackOut(BaseModel):
    id: StrictStr
    user_id: StrictStr
    latitude: StrictStr
    longitude: StrictStr
    timestamp: datetime
