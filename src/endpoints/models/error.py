from pydantic import BaseModel, StrictStr


class Error(BaseModel):
    message: StrictStr
