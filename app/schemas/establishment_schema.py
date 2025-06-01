from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base_schema import BaseSchema # ou TunedModel se preferir

class EstablishmentBase(BaseModel):
    name: str
    phone_number: Optional[str] = None
    # working_hours_config: Optional[dict] = None

class EstablishmentCreate(EstablishmentBase):
    pass

class EstablishmentInDBBase(EstablishmentBase):
    id: int
    user_id: int
    created_at: datetime
    # updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Establishment(EstablishmentInDBBase):
    pass