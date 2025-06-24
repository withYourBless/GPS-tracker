from pydantic import BaseModel, StrictStr


class LoginRequest(BaseModel):
    email: StrictStr
    password: StrictStr
