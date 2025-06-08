from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base_schema import BaseSchema # ou TunedModel se preferir
from .working_hours_schema import WorkingHoursConfig

class EstablishmentBase(BaseModel):
    name: str
    phone_number: Optional[str] = None
    working_hours_config: Optional[WorkingHoursConfig] = None

# Schema para criar um novo Establishment
class EstablishmentCreate(EstablishmentBase):
    # Se working_hours_config é opcional na criação, pode ser None
    # Se quisermos que seja obrigatório na criação, removemos o Optional aqui
    # ou definimos um valor default no Pydantic/modelo se aplicável.
    # Por agora, vamos manter opcional na criação.
    pass

# Schema para atualizar um Establishment (adicionaremos depois, similar ao ServiceUpdate)
class EstablishmentUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    working_hours_config: Optional[WorkingHoursConfig] = None
 

class EstablishmentInDBBase(EstablishmentBase):
    id: int
    user_id: int
    created_at: datetime
    # updated_at: Optional[datetime]

    class Config:
        orm_mode = True

# Schema para retornar um Establishment do banco de dados
class Establishment(BaseSchema):
    id: int
    name: str
    phone_number: Optional[str] = None
    timezone: str
    # Adicionamos working_hours_config: Optional[WorkingHoursConfig] = None aos schemas. Isso significa que o campo é opcional e, se fornecido, deve seguir a estrutura definida em WorkingHoursConfig.
    working_hours_config: Optional[WorkingHoursConfig] = None # ADICIONADO AQUI
    user_id: int
    created_at: datetime
    # updated_at: Optional[datetime] # Se você tiver este campo