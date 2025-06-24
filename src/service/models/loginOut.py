from pydantic import BaseModel, StrictStr


class LoginOut(BaseModel):
    email: StrictStr
    status: StrictStr
