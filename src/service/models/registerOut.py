from pydantic import BaseModel, StrictStr


class RegisterOut(BaseModel):
    id: StrictStr
    name: StrictStr
    email: StrictStr
    role: StrictStr
    register_date: StrictStr
