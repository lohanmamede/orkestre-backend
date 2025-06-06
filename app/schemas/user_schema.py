from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .base_schema import BaseSchema # ou TunedModel se preferir
from .working_hours_schema import WorkingHoursConfig

# Propriedades básicas que um usuário tem (para leitura)
class UserBase(BaseModel):
    email: EmailStr

# Propriedades recebidas na criação de um usuário
class UserCreate(UserBase):
    password: str
    establishment_name: str

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

"""
Novo schema para a resposta do endpoint /users/me
Sub-schema para não expor todos os 
detalhes do estabelecimento, apenas o id e name por enquanto (podemos ajustar depois). Ele precisa ter orm_mode = True (ou from_attributes = True, dependendo do seu BaseSchema).
"""
class EstablishmentForUserMe(BaseModel):
    id: int
    name: str # Podemos adicionar mais campos do estabelecimento se necessário
    working_hours_config: Optional[WorkingHoursConfig] = None # Adicione
    class Config:
        orm_mode = True # ou from_attributes = True

""" 
Schema para o endpoint /users/me
Este será o schema de resposta. Ele inclui os campos básicos do usuário e um campo opcional establishment do tipo EstablishmentForUserMe.
"""
class UserMe(BaseSchema): # Herda de BaseSchema para ter from_attributes = True
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    establishment: Optional[EstablishmentForUserMe] = None # Inclui o ID e nome do estabelecimento






