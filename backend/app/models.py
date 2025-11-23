from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Request Model for creating a device
class DeviceCreate(BaseModel):
    inventory_no: str
    devicetype_id: int
    location_id: Optional[int] = None
    model: Optional[str] = None

# Request Model for creating an assignment
class AssignmentCreate(BaseModel):
    device_id: int
    personnel_no: int
    assigned_from: Optional[datetime] = None