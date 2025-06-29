# app/schemas/establishment_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from .base_schema import BaseSchema
from app.models.role_enum import Role

# --- Schema para representar um membro na resposta da API ---
class MemberSchema(BaseSchema):
    id: int
    email: EmailStr
    role: Role

# --- Schemas para o fluxo de CRUD do Estabelecimento ---

class EstablishmentBase(BaseModel):
    name: str
    phone_number: Optional[str] = None
    timezone: Optional[str] = "America/Sao_Paulo"
    display_address: Optional[str] = None
    about_text: Optional[str] = None
    # Adicione aqui outros campos que o dono possa editar no seu perfil de estabelecimento

class EstablishmentUpdate(EstablishmentBase):
    # Para atualizar, todos os campos são opcionais
    name: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    display_address: Optional[str] = None
    about_text: Optional[str] = None
    # Herdamos de EstablishmentBase, mas podemos redefinir para serem todos opcionais.
    # Uma forma mais explícita:
    # name: Optional[str] = None
    # etc...

class CollaboratorCreate(BaseModel):
    """Schema para o corpo da requisição ao adicionar um novo colaborador."""
    email: EmailStr

# --- Schema principal de resposta da API para Establishment ---
class Establishment(BaseSchema):
    id: int
    name: str
    phone_number: Optional[str] = None
    timezone: str
    display_address: Optional[str] = None
    about_text: Optional[str] = None

    users: List[MemberSchema] = [] # A lista de membros com seus papéis