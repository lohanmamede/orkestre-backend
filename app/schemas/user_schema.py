from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .base_schema import BaseSchema # ou TunedModel se preferir

# Propriedades básicas que um usuário tem (para leitura)
class UserBase(BaseModel):
    email: EmailStr

# Propriedades recebidas na criação de um usuário
class UserCreate(UserBase):
    password: str

# Propriedades adicionais armazenadas no DB, mas não necessariamente retornadas sempre
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # updated_at: Optional[datetime] # Removido updated_at para simplificar o retorno inicial

    class Config: # Herdando de BaseModel, precisamos redefinir Config se quisermos orm_mode
        # orm_mode = True # Linha antiga
        from_attributes = True # Nova linha para Pydantic V2+

# Propriedades retornadas pela API (não inclui o password)
class User(UserInDBBase):
    pass # Herda tudo de UserInDBBase

# Schema para login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None






