from datetime import datetime

from pydantic import BaseModel, StrictStr


class RegisterResponse(BaseModel):
    id: StrictStr
    name: StrictStr
    email: StrictStr
    role: StrictStr
    register_date: datetime
