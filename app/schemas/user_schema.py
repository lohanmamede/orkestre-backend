# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, model_validator 
from typing import Optional, List, Any # Adicione List
from datetime import datetime

from app.models.role_enum import Role # Importe o Enum de Role
from .base_schema import BaseSchema


# --- Schemas para o fluxo de Autenticação ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    # Ambos são agora totalmente opcionais. Um usuário pode se cadastrar sem nenhum deles.
    establishment_name: Optional[str] = None
    invite_code: Optional[str] = None # Manteremos para uma futura implementação de convites se quisermos

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Schemas de Resposta (como a API retorna os dados) ---

# Um sub-schema para representar a associação de um usuário a um estabelecimento
class UserEstablishmentInfo(BaseSchema):
    id: int
    name: str
    role: Role

# O novo schema de resposta para o endpoint /users/me
class UserMe(BaseSchema):
    id: int
    email: EmailStr
    is_active: bool
    establishments: List[UserEstablishmentInfo] = [] # Agora é uma lista de associações

# O schema genérico de usuário para outras respostas (pode ou não incluir os estabelecimentos)
class User(BaseSchema):
    id: int
    email: EmailStr
    is_active: bool