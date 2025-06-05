from sqlalchemy.orm import Session
from sqlalchemy import and_ # Para construir queries com múltiplas condições
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.appointment_model import Appointment, AppointmentStatus
from app.models.establishment_model import Establishment
from app.models.service_model import Service
from app.schemas.appointment_schema import AppointmentCreate
from app.schemas.working_hours_schema import WorkingHoursConfig, DayWorkingHours # Nossos schemas de horário

from sqlalchemy import desc # Para ordenar
from datetime import date # Para o filtro de data

# --- FUNÇÕES CRUD E LÓGICA PARA AGENDAMENTOS ---

def _calculate_end_time(start_time: datetime, duration_minutes: int) -> datetime:
    """Calcula o horário de término com base no início e na duração."""
    return start_time + timedelta(minutes=duration_minutes)

def _is_slot_available(
    db: Session,
    establishment_id: int,
    proposed_start_time: datetime,
    proposed_end_time: datetime
) -> bool:
    """
    Verifica se um slot de horário está disponível em um estabelecimento,
    considerando outros agendamentos já existentes.
    """
    # Busca por agendamentos existentes que se sobreponham ao horário proposto
    # Um slot está ocupado se:
    # (outro.start_time < proposed_end_time) AND (outro.end_time > proposed_start_time)
    # Consideramos apenas agendamentos PENDING ou CONFIRMED como bloqueadores
    overlapping_appointments = db.query(Appointment).filter(
        Appointment.establishment_id == establishment_id,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
        Appointment.start_time < proposed_end_time,
        Appointment.end_time > proposed_start_time
    ).count()

    return overlapping_appointments == 0

def _is_within_working_hours(
    proposed_start_time: datetime,
    proposed_end_time: datetime,
    working_hours_day_config: DayWorkingHours # Config do dia da semana específico
) -> bool:
    """
    Verifica se o slot proposto está dentro do horário de funcionamento
    e fora dos intervalos de pausa para um dia específico.
    """
    if not working_hours_day_config.is_active:
        return False # Dia inativo

    day_start_str = working_hours_day_config.start_time
    day_end_str = working_hours_day_config.end_time
    lunch_start_str = working_hours_day_config.lunch_break_start_time
    lunch_end_str = working_hours_day_config.lunch_break_end_time

    # Converte os horários de string (HH:MM) para objetos time para comparação
    # (Assumindo que proposed_start_time e proposed_end_time são datetimes completos)
    # E que os horários no config são apenas HH:MM

    # Simplificação: Se não houver horário de início ou fim para o dia, consideramos fechado
    if not day_start_str or not day_end_str:
        return False

    # Compara apenas a parte de hora/minuto
    # É importante que proposed_start_time e proposed_end_time estejam no mesmo dia
    # e que esse dia corresponda ao working_hours_day_config

    # Converte HH:MM string para time object para fácil comparação
    # A data será a mesma do proposed_start_time para consistência
    date_of_appointment = proposed_start_time.date()

    day_start_dt = datetime.combine(date_of_appointment, datetime.strptime(day_start_str, "%H:%M").time(), tzinfo=proposed_start_time.tzinfo)
    day_end_dt = datetime.combine(date_of_appointment, datetime.strptime(day_end_str, "%H:%M").time(), tzinfo=proposed_start_time.tzinfo)

    # Verifica se está dentro do horário de funcionamento do dia
    if not (day_start_dt <= proposed_start_time and proposed_end_time <= day_end_dt):
        return False

    # Verifica se colide com a pausa para almoço (se houver)
    if lunch_start_str and lunch_end_str:
        lunch_start_dt = datetime.combine(date_of_appointment, datetime.strptime(lunch_start_str, "%H:%M").time(), tzinfo=proposed_start_time.tzinfo)
        lunch_end_dt = datetime.combine(date_of_appointment, datetime.strptime(lunch_end_str, "%H:%M").time(), tzinfo=proposed_start_time.tzinfo)

        # O agendamento não pode sobrepor a pausa
        # Não pode começar durante a pausa, nem terminar durante a pausa, nem englobar a pausa
        if (proposed_start_time < lunch_end_dt and proposed_end_time > lunch_start_dt):
            return False

    return True


def create_appointment(
    db: Session, *, appointment_in: AppointmentCreate, establishment_id: int
) -> Appointment: # Retorna o objeto Appointment criado
    """
    Cria um novo agendamento após verificar a disponibilidade.
    """
    # 1. Buscar o estabelecimento
    establishment = db.query(Establishment).filter(Establishment.id == establishment_id).first()
    if not establishment:
        raise ValueError(f"Estabelecimento com ID {establishment_id} não encontrado.") # Usaremos HTTPException no endpoint

    # 2. Buscar o serviço para obter a duração
    service = db.query(Service).filter(Service.id == appointment_in.service_id).first()
    if not service:
        raise ValueError(f"Serviço com ID {appointment_in.service_id} não encontrado.")
    if service.establishment_id != establishment_id: # Verifica se o serviço pertence ao estabelecimento
         raise ValueError(f"Serviço com ID {appointment_in.service_id} não pertence ao estabelecimento {establishment_id}.")
    if not service.is_active:
        raise ValueError(f"Serviço com ID {appointment_in.service_id} não está ativo.")

    # 3. Calcular o horário de término
    proposed_start_time = appointment_in.start_time
    duration_minutes = service.duration_minutes
    proposed_end_time = _calculate_end_time(proposed_start_time, duration_minutes)

    # 4. Verificar a configuração de horários do estabelecimento
    if not establishment.working_hours_config:
        raise ValueError("Estabelecimento não possui configuração de horários de atendimento.")

    # Pydantic pode parsear o JSON do banco para o nosso schema WorkingHoursConfig
    try:
        working_hours = WorkingHoursConfig.parse_obj(establishment.working_hours_config)
    except Exception as e: # Se o JSON no banco estiver malformado (não deveria acontecer se salvamos via Pydantic)
        print(f"Erro ao parsear working_hours_config: {e}") # Logar o erro
        raise ValueError("Erro interno ao processar horários de atendimento do estabelecimento.")

    # Determinar o dia da semana (0=Segunda, 1=Terça, ..., 6=Domingo)
    day_of_week_int = proposed_start_time.weekday()
    days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_key = days_map[day_of_week_int]

    day_config: DayWorkingHours = getattr(working_hours, day_key)

    # 5. Verificar se está dentro do horário de funcionamento e fora de pausas
    if not _is_within_working_hours(proposed_start_time, proposed_end_time, day_config):
        raise ValueError(f"O horário solicitado está fora do horário de funcionamento ou em horário de pausa para {day_key.capitalize()}.")

    # 6. Verificar se o slot de horário está livre (não colide com outros agendamentos)
    if not _is_slot_available(db, establishment_id, proposed_start_time, proposed_end_time):
        raise ValueError("O horário solicitado já está ocupado.")

    # 7. Se tudo estiver OK, criar o agendamento
    db_appointment = Appointment(
        start_time=proposed_start_time,
        end_time=proposed_end_time,
        customer_name=appointment_in.customer_name,
        customer_phone=appointment_in.customer_phone,
        customer_email=appointment_in.customer_email,
        notes_by_customer=appointment_in.notes_by_customer,
        status=AppointmentStatus.PENDING, # Ou CONFIRMED, dependendo da regra de negócio
        establishment_id=establishment_id,
        service_id=appointment_in.service_id
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Outras funções de serviço (get, update, delete para appointments) virão aqui...

def get_appointment(db: Session, *, appointment_id: int, establishment_id: int) -> Optional[Appointment]:
    """
    Obtém um agendamento específico pelo seu ID,
    garantindo que ele pertença ao estabelecimento fornecido.
    """
    return db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.establishment_id == establishment_id
    ).first()
 
   
def get_appointments_by_establishment(
    db: Session, 
    *, 
    establishment_id: int, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None, # Filtro opcional por data de início
    end_date: Optional[date] = None,   # Filtro opcional por data de fim
    status: Optional[AppointmentStatus] = None # Filtro opcional por status
) -> List[Appointment]:
    """
    Obtém uma lista de agendamentos para um estabelecimento específico,
    com paginação e filtros opcionais.
    """
    query = db.query(Appointment).filter(Appointment.establishment_id == establishment_id)

    if start_date:
        # Filtra agendamentos cuja start_time seja maior ou igual a start_date
        # Converte start_date para datetime no início do dia
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(Appointment.start_time >= start_datetime)
    
    if end_date:
        # Filtra agendamentos cuja start_time seja menor que o dia seguinte a end_date
        # Converte end_date para datetime no final do dia (ou início do dia seguinte)
        end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
        query = query.filter(Appointment.start_time < end_datetime)

    if status:
        query = query.filter(Appointment.status == status)
        
    # Ordena pelos mais recentes primeiro (ou por start_time)
    return query.order_by(desc(Appointment.start_time)).offset(skip).limit(limit).all()

# Função de Serviço e Endpoint para Atualizar o Status de um Agendamento
def update_appointment_status(
    db: Session, *, appointment_db_obj: Appointment, status_in: AppointmentStatus
) -> Appointment:
    """
    Atualiza o status de um agendamento existente.
    """
    appointment_db_obj.status = status_in
    db.add(appointment_db_obj)
    db.commit()
    db.refresh(appointment_db_obj)
    return appointment_db_obj



"""
Explicação Detalhada da Função create_appointment e suas Auxiliares:

- Funções Auxiliares (prefixadas com _):
    - _calculate_end_time(...): Simples, calcula o horário de término somando a duration_minutes ao start_time.
    - _is_within_working_hours(...):
        - Recebe o horário proposto e a configuração DayWorkingHours para o dia específico da semana do agendamento.
        - Verifica se o dia está ativo (is_active).
        - Converte as strings de horário (ex: "09:00") do DayWorkingHours para objetos datetime (usando a data do agendamento proposto para consistência na comparação).
        - Checa se o agendamento proposto (proposed_start_time e proposed_end_time) está completamente dentro do day_start_dt e day_end_dt.
        - Checa se o agendamento proposto colide com o intervalo de almoço (lunch_start_dt e lunch_end_dt), se houver.
    - _is_slot_available(...):
        - Busca no banco por quaisquer agendamentos existentes (PENDING ou CONFIRMED) para o mesmo establishment_id que se sobreponham ao intervalo do proposed_start_time e proposed_end_time.
        - A lógica de sobreposição é: outro_agendamento.start_time < proposed_end_time E outro_agendamento.end_time > proposed_start_time.
        - Se encontrar algum (count() > 0), o slot não está disponível.

Função Principal create_appointment(...):
1. Busca o Establishment e o Service para garantir que existem, que o serviço pertence ao estabelecimento e está ativo.
2. Calcula o proposed_end_time usando _calculate_end_time.
3. Busca a working_hours_config do estabelecimento. Se não existir, levanta um erro.
4. Usa WorkingHoursConfig.parse_obj() para converter o JSON do banco de volta para nosso objeto Pydantic, permitindo fácil acesso e validação.
5. Determina o dia da semana do agendamento (ex: "monday") e pega a configuração específica para aquele dia (day_config).
6. Chama _is_within_working_hours para verificar se o horário está dentro do expediente e fora de pausas. Se não, levanta um erro.
7. Chama _is_slot_available para verificar se não há colisão com outros agendamentos. Se não, levanta um erro.
8. Se todas as verificações passarem, cria o novo objeto Appointment com os dados fornecidos e o status inicial (ex: PENDING).
9. Salva no banco e retorna o agendamento criado.

Função get_appointment:
O que faz: 
- Busca um agendamento pelo appointment_id, mas também verifica se ele pertence ao establishment_id correto. Isso é importante para garantir que um profissional só possa ver detalhes de agendamentos do seu próprio estabelecimento.

Função get_appointments_by_establishment:
O que faz:
- Busca todos os agendamentos para um establishment_id específico.
- Inclui skip e limit para paginação.
- Adiciona filtros opcionais por start_date, end_date e status. Isso será muito útil para o profissional visualizar sua agenda (ex: "agendamentos de hoje", "agendamentos confirmados da próxima semana").
- Ordena os resultados (exemplo: pelos mais recentes ou pelo horário de início).

Importante:
- Tratamento de Erros: As funções estão levantando ValueError por enquanto. Nos endpoints da API, precisaremos capturar esses ValueError e convertê-los em HTTPException apropriadas (ex: 400 Bad Request, 404 Not Found, 409 Conflict) com mensagens claras para o frontend.
- Fuso Horário (Timezone): É crucial que os datetimes sejam tratados consistentemente com fuso horário (o timezone=True nos modelos SQLAlchemy e a forma como o frontend envia o start_time são importantes). O datetime.utcnow() não tem fuso horário por padrão, então é melhor usar datetime.now(timezone.utc) ou garantir que o banco e a aplicação estejam configurados para UTC. Por agora, a lógica de comparação de horários dentro de _is_within_working_hours assume que todos os datetimes estão no mesmo fuso ou são comparáveis.
- Intervalo de Agendamento (appointmentIntervalMinutes): A lógica de gerar slots disponíveis para o cliente escolher ainda não está aqui. Esta função create_appointment assume que o cliente já escolheu um start_time específico. A lógica para mostrar os slots (ex: 09:00, 09:30, 10:00) com base no appointmentIntervalMinutes e na disponibilidade será outra parte importante.
"""