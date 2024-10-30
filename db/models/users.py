from typing import Optional
from pydantic import BaseModel

class Users(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    rol_id: str