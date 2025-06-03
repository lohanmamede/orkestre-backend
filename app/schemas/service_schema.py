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
    
    """
    Explicação dos Schemas:

    ServiceBase(BaseModel):
        - Contém os campos comuns que definem um serviço: name, description, price, duration_minutes, is_active.
        - is_active tem um valor padrão True, então se não for fornecido na criação, o serviço será ativo.
        - Não precisa herdar de BaseSchema porque ele é usado como base para ServiceCreate, que é para entrada de dados, não leitura direta de um objeto ORM.
    ServiceCreate(ServiceBase):
        - Herda todos os campos de ServiceBase. É o que esperamos receber no corpo da requisição quando um profissional for cadastrar um novo serviço.
        - Não incluímos establishment_id aqui porque geralmente o endpoint de criação de serviço já estará no contexto de um estabelecimento (ex: /establishments/{establishment_id}/services/) ou pegaremos o establishment_id do usuário logado.
    ServiceUpdate(BaseModel):
        - Usado para atualizar um serviço existente. Todos os campos são Optional porque o usuário pode querer atualizar apenas um ou alguns deles, não todos.
    Service(BaseSchema):
        - Este é o schema que nossa API usará para retornar os dados de um serviço.
        - Ele herda de BaseSchema para que o from_attributes = True (o antigo orm_mode) seja aplicado, permitindo que ele seja preenchido diretamente a partir de um objeto Service do SQLAlchemy.
        - Inclui todos os campos de ServiceBase mais o id do serviço, o establishment_id ao qual ele pertence, e os timestamps created_at e updated_at.
    """