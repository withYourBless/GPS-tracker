from datetime import datetime

from pydantic import BaseModel, StrictStr


class UserOut(BaseModel):
    name: StrictStr
    email: StrictStr
    role: StrictStr
    register_date: datetime
