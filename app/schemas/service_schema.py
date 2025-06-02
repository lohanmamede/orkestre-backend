from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .base_schema import BaseSchema # Importa nossa BaseSchema com from_attributes = True

# Propriedades básicas de um serviço
class ServiceBase(BaseModel): # Não precisa herdar de BaseSchema se for só para entrada/validação base
    name: str
    description: Optional[str] = None
    price: float
    duration_minutes: int
    is_active: Optional[bool] = True # Default True na criação se não fornecido

# Schema para criar um novo serviço (o que o frontend envia)
# establishment_id será fornecido no path do endpoint ou pego do usuário logado,
# não precisa estar no corpo da requisição de criação do serviço em si.
class ServiceCreate(ServiceBase):
    pass

# Schema para atualizar um serviço (todos os campos são opcionais)
class ServiceUpdate(BaseModel): # Não precisa herdar de BaseSchema, pois é para entrada PATCH/PUT
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

# Schema para retornar um serviço pela API (o que a API envia de volta)
class Service(BaseSchema): # Herda de BaseSchema para ter from_attributes = True
    id: int
    name: str
    description: Optional[str] = None
    price: float
    duration_minutes: int
    is_active: bool
    establishment_id: int # Para sabermos a qual estabelecimento ele pertence
    created_at: datetime
    updated_at: Optional[datetime] = None # Consistente com nossos modelos