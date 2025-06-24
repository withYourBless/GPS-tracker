from pydantic import BaseModel, StrictStr


class LoginResponse(BaseModel):
    token: StrictStr
