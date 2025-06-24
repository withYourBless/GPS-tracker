from pydantic import BaseModel, StrictStr


class RegisterRequest(BaseModel):
    name: StrictStr
    email: StrictStr
    password: StrictStr
