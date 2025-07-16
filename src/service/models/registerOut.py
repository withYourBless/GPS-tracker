from datetime import datetime

from pydantic import BaseModel, StrictStr


class RegisterOut(BaseModel):
    id: StrictStr
    name: StrictStr
    email: StrictStr
    role: StrictStr
    register_date: datetime

    model_config = {
        "from_attributes": True
    }
