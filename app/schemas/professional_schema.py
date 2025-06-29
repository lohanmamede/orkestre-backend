# app/schemas/professional_schema.py
from pydantic import BaseModel
from typing import Optional

from .base_schema import BaseSchema

class ProfessionalBase(BaseModel):
    name: str

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalUpdate(ProfessionalBase):
    name: Optional[str] = None

class Professional(BaseSchema):
    id: int
    name: str
    establishment_id: int