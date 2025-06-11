from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum # Para o Enum do status

from app.db.base_class import Base # Importe a classe Base

# Enum para o status do agendamento
class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED_BY_CLIENT = "cancelled_by_client"
    CANCELLED_BY_ESTABLISHMENT = "cancelled_by_establishment"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class Appointment(Base):
    # __tablename__ será 'appointments'
    id = Column(Integer, primary_key=True, index=True)

    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False) # Calculado: start_time + service_duration

    # Informações do Cliente
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False, index=True) # Importante para lembretes/contato
    customer_email = Column(String, nullable=True, index=True)
    notes_by_customer = Column(Text, nullable=True) # Observações do cliente ao agendar

    # Informações do Profissional/Estabelecimento
    notes_by_establishment = Column(Text, nullable=True) # Observações internas do estabelecimento
    status = Column(SAEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING, index=True)

    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Chaves Estrangeiras e Relacionamentos
    establishment_id = Column(Integer, ForeignKey("establishments.id"), nullable=False)
    establishment = relationship("Establishment") # Relacionamento simples, sem back_populates por enquanto se não for estritamente necessário no Establishment

    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    service = relationship("Service") # Relacionamento simples

    # Timestamps padrão
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    
"""
Explicação dos Campos do Modelo Appointment:

- AppointmentStatus(str, enum.Enum): Criamos um Enum Python para definir os possíveis status de um agendamento. Usar um Enum torna o código mais legível e seguro contra erros de digitação nos status. O SAEnum do SQLAlchemy o traduz para um tipo de enumeração no banco (ou string).
- start_time, end_time: Timestamps com fuso horário para o início e fim do agendamento. O end_time será calculado com base na duração do serviço.
- customer_name, customer_phone, customer_email: Informações do cliente que está fazendo o agendamento. O telefone é marcado como obrigatório.
- notes_by_customer: Um campo para o cliente adicionar alguma observação ao agendar.
- notes_by_establishment: Um campo para o profissional adicionar notas internas sobre aquele agendamento.
- status: O status atual do agendamento, usando nosso Enum AppointmentStatus (o padrão é "pending").
- establishment_id, service_id: Chaves estrangeiras que ligam o agendamento ao estabelecimento e ao serviço específico que foi agendado.
- establishment, service: Relacionamentos SQLAlchemy para podermos acessar facilmente os objetos Establishment e Service a partir de um objeto Appointment (ex: meu_agendamento.service.name). Para estes relacionamentos simples de "leitura" a partir do agendamento, não precisamos necessariamente de back_populates nos modelos Establishment e Service, a menos que queiramos navegar de Establishment para todos os seus Appointments (o que pode ser útil no futuro para o dashboard do profissional). Por agora, vamos manter simples. Se precisarmos do back_populates depois, adicionaremos.
"""