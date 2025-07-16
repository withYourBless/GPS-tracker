from pydantic import BaseModel, StrictStr


class LoginIn(BaseModel):
    email: StrictStr
    password: StrictStr
