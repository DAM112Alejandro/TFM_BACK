from pydantic import BaseModel

class WorkTypes(BaseModel):
    description: str
    time: int #100 = 1hora
    