from datetime import datetime

from pydantic import BaseModel, StrictStr


class UserResponse(BaseModel):
    name: StrictStr
    email: StrictStr
    role: StrictStr
    register_date: datetime
