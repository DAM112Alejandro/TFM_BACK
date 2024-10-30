from pydantic import BaseModel
import datetime

class Jobs(BaseModel):
    registration_date: datetime
    appointment_date: datetime
    start_date: datetime
    finish_date: datetime
    license_plate: str
    client_phone: str
    user_id: str
    status_id: str
    workType_id: str

    class Config:
        arbitrary_types_allowed = True
