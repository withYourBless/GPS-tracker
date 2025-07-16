from pydantic import BaseModel, StrictStr


class RegisterIn(BaseModel):
    name: StrictStr
    email: StrictStr
    password: StrictStr
