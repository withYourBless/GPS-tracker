from typing import Optional, List

from pydantic import BaseModel

from src.endpoints.models.userResponse import UserResponse


class UsersResponse(BaseModel):
    users: Optional[List[UserResponse]] = None
