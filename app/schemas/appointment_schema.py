from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.models.appointment_model import AppointmentStatus # Importa o Enum do status
from .base_schema import BaseSchema # Nossa BaseSchema com from_attributes = True

# Propriedades básicas de um agendamento que podem ser compartilhadas
class AppointmentBase(BaseModel):
    start_time: datetime
    # end_time será calculado ou também recebido, dependendo da lógica
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=10, max_length=20) # Exemplo de validação de tamanho
    customer_email: Optional[EmailStr] = None
    notes_by_customer: Optional[str] = None
    service_id: int # O ID do serviço que está sendo agendado

# Schema para criar um novo agendamento (o que o cliente final envia)
# establishment_id geralmente virá do path da URL
# end_time será calculado no backend com base no start_time e na duração do serviço
# status terá um default no backend (ex: PENDING)
class AppointmentCreate(AppointmentBase):
    pass # Herda tudo de AppointmentBase, o que é suficiente para a criação pelo cliente

# Schema para atualizar um agendamento (o que o profissional pode mudar)
class AppointmentUpdate(BaseModel): # Não herda de BaseSchema se for só para entrada
    start_time: Optional[datetime] = None
    # end_time: Optional[datetime] = None # Geralmente recalculado se start_time ou serviço mudar
    status: Optional[AppointmentStatus] = None
    notes_by_establishment: Optional[str] = None
    # Outros campos que o profissional pode atualizar...

# Schema para retornar um agendamento pela API (o que a API envia de volta)
class Appointment(BaseSchema): # Herda de BaseSchema para ter from_attributes = True
    id: int
    start_time: datetime
    end_time: datetime # Importante ter no retorno
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    notes_by_customer: Optional[str] = None
    notes_by_establishment: Optional[str] = None
    status: AppointmentStatus

    establishment_id: int
    service_id: int

    created_at: datetime
    updated_at: Optional[datetime] = None

    # Opcional: Incluir detalhes do serviço ou estabelecimento se necessário no retorno
    # service: Optional[ServiceSchema] # Se tivermos um ServiceSchema definido
    # establishment: Optional[EstablishmentSchema] # Se tivermos um EstablishmentSchema
 
# Schema para atualizar o status de um agendamento   
class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

"""
Explicação dos Schemas:

- AppointmentBase(BaseModel):
    - Contém os campos que são a base para um agendamento, principalmente os que o cliente final forneceria: start_time (o cliente escolhe quando quer começar), customer_name, customer_phone, customer_email (opcional), notes_by_customer (opcional), e crucialmente, o service_id do serviço desejado.
    - Adicionei Field(..., min_length=..., max_length=...) como exemplo de validações que o Pydantic pode fazer.
- AppointmentCreate(AppointmentBase):
    - Herda de AppointmentBase. Para o MVP, os dados que o cliente envia para criar um agendamento são esses.
    - Não incluímos establishment_id aqui porque ele virá do contexto do endpoint (ex: /establishments/{establishment_id}/appointments).
    - Não incluímos end_time aqui porque ele será calculado no backend (usando o start_time + service.duration_minutes).
    - Não incluímos status aqui porque ele terá um valor padrão no backend (ex: AppointmentStatus.PENDING) quando um novo agendamento for criado.
- AppointmentUpdate(BaseModel):
    - Usado quando um profissional (ou talvez um cliente, dependendo das regras) for atualizar um agendamento.
    - Campos como start_time, status, notes_by_establishment são opcionais, pois apenas alguns deles podem ser atualizados por vez.
- Appointment(BaseSchema):
    - Este é o schema que nossa API usará para retornar os dados de um agendamento.
    - Herda de BaseSchema para que o from_attributes = True seja aplicado.
    - Inclui todos os campos relevantes do agendamento que queremos mostrar, como id, start_time, end_time (importante ter aqui), todos os dados do cliente, notas, status, e os IDs de establishment e service.
    - Deixei um comentário sobre a possibilidade de, no futuro, aninhar os detalhes completos do serviço ou do estabelecimento aqui usando outros schemas, se necessário.
"""