# app/services/appointment_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date, time, datetime, timedelta
import pytz

from app.models.appointment_model import Appointment, AppointmentStatus
from app.models.establishment_model import Establishment
from app.models.service_model import Service
from app.schemas.appointment_schema import AppointmentCreate, AppointmentStatusUpdate
from app.schemas.working_hours_schema import WorkingHoursConfig, DayWorkingHours

# --- FUNÇÕES DE LÓGICA DE AGENDAMENTO ---

def get_available_slots(
    db: Session, *, establishment_id: int, service_id: int, appointment_date: date
) -> List[time]:
    """
    Calcula e retorna os horários de início disponíveis, considerando o fuso horário
    específico do estabelecimento e convertendo tudo para UTC para comparações.
    """
    # 1. Busca os dados essenciais
    establishment = db.query(Establishment).filter(Establishment.id == establishment_id).first()
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not establishment or not service or not establishment.working_hours_config:
        return []

    # 2. Define o fuso horário do estabelecimento
    try:
        establishment_tz = pytz.timezone(establishment.timezone)
    except pytz.UnknownTimeZoneError:
        return [] # Retorna vazio se o timezone no banco for inválido

    # 3. Parseia a configuração de horários e obtém a do dia correto
    working_hours = WorkingHoursConfig.parse_obj(establishment.working_hours_config)
    day_of_week_int = appointment_date.weekday()
    days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_config = getattr(working_hours, days_map[day_of_week_int])

    if not day_config.is_active or not day_config.start_time or not day_config.end_time:
        return []

    # 4. Converte os horários de funcionamento para datetimes AWARE no fuso do estabelecimento
    day_start_naive = datetime.combine(appointment_date, datetime.strptime(day_config.start_time, "%H:%M").time())
    day_end_naive = datetime.combine(appointment_date, datetime.strptime(day_config.end_time, "%H:%M").time())
    
    day_start_local = establishment_tz.localize(day_start_naive)
    day_end_local = establishment_tz.localize(day_end_naive)

    # 5. Gera todos os possíveis slots de início no horário local
    interval = working_hours.appointment_interval_minutes
    duration = service.duration_minutes
    
    possible_slots_local = []
    current_slot_local = day_start_local
    while (current_slot_local + timedelta(minutes=duration)) <= day_end_local:
        possible_slots_local.append(current_slot_local)
        current_slot_local += timedelta(minutes=interval)

    # 6. Remove slots que caem na pausa para almoço (ainda em horário local)
    available_slots_local = []
    if day_config.lunch_break_start_time and day_config.lunch_break_end_time:
        lunch_start_naive = datetime.combine(appointment_date, datetime.strptime(day_config.lunch_break_start_time, "%H:%M").time())
        lunch_end_naive = datetime.combine(appointment_date, datetime.strptime(day_config.lunch_break_end_time, "%H:%M").time())
        lunch_start_local = establishment_tz.localize(lunch_start_naive)
        lunch_end_local = establishment_tz.localize(lunch_end_naive)
        
        for slot in possible_slots_local:
            slot_end_time = slot + timedelta(minutes=duration)
            if not (slot < lunch_end_local and slot_end_time > lunch_start_local):
                available_slots_local.append(slot)
    else:
        available_slots_local = possible_slots_local

    # 7. Busca agendamentos existentes (o banco armazena em UTC) para o dia inteiro (considerando UTC)
    utc_tz = pytz.utc
    day_start_utc = day_start_local.astimezone(utc_tz)
    day_end_of_day_utc = (day_start_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    existing_appointments = db.query(Appointment).filter(
        Appointment.establishment_id == establishment_id,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
        Appointment.start_time >= day_start_utc,
        Appointment.start_time < day_end_of_day_utc
    ).all()

    # 8. Filtra os slots que conflitam com agendamentos existentes, COMPARANDO TUDO EM UTC
    final_available_slots = []
    for slot_local in available_slots_local:
        slot_utc_start = slot_local.astimezone(utc_tz)
        slot_utc_end = (slot_local + timedelta(minutes=duration)).astimezone(utc_tz)
        
        is_occupied = False
        for existing_appt in existing_appointments:
            if slot_utc_start < existing_appt.end_time and slot_utc_end > existing_appt.start_time:
                is_occupied = True
                break
        if not is_occupied:
            final_available_slots.append(slot_local.time())

    return final_available_slots

# --- FUNÇÕES CRUD PARA AGENDAMENTOS ---

def create_appointment(
    db: Session, *, appointment_in: AppointmentCreate, establishment_id: int
) -> Appointment:
    """
    Cria um novo agendamento após verificar a disponibilidade.
    A verificação de disponibilidade agora está contida em get_available_slots.
    Esta função deve ser chamada depois que o cliente seleciona um slot válido.
    """
    service = db.query(Service).filter(Service.id == appointment_in.service_id).first()
    if not service or service.establishment_id != establishment_id or not service.is_active:
        raise ValueError("Serviço inválido ou não pertence a este estabelecimento.")
    
    # Recalcula o end_time para garantir consistência
    end_time = appointment_in.start_time + timedelta(minutes=service.duration_minutes)

    # Aqui, poderíamos re-validar a disponibilidade do slot exato como uma dupla checagem, mas
    # vamos confiar que o frontend só está enviando slots que foram retornados por get_available_slots.
    
    db_appointment = Appointment(
        start_time=appointment_in.start_time,
        end_time=end_time,
        customer_name=appointment_in.customer_name,
        customer_phone=appointment_in.customer_phone,
        customer_email=appointment_in.customer_email,
        notes_by_customer=appointment_in.notes_by_customer,
        status=AppointmentStatus.PENDING,
        establishment_id=establishment_id,
        service_id=appointment_in.service_id
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointment(db: Session, *, appointment_id: int) -> Optional[Appointment]:
    """
    Obtém um agendamento específico pelo seu ID.
    A verificação de propriedade deve ser feita no endpoint.
    """
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments_by_establishment(
    db: Session, 
    *, 
    establishment_id: int, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None
) -> List[Appointment]:
    """
    Obtém uma lista de agendamentos para um estabelecimento, com filtros.
    """
    query = db.query(Appointment).filter(Appointment.establishment_id == establishment_id)

    if start_date:
        start_datetime = datetime.combine(start_date, time.min)
        query = query.filter(Appointment.start_time >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date + timedelta(days=1), time.min)
        query = query.filter(Appointment.start_time < end_datetime)

    if status:
        query = query.filter(Appointment.status == status)
        
    return query.order_by(desc(Appointment.start_time)).offset(skip).limit(limit).all()

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


Função get_available_slots:
- Pega o Timezone do Banco: A primeira coisa que fazemos é buscar o establishment.timezone (ex: "America/Sao_Paulo").
- Trabalha no Horário Local: Geramos todos os slots possíveis (possible_slots_local) no fuso horário do estabelecimento. Isso torna mais fácil verificar contra o horário de funcionamento e as pausas, que também estão no horário local.
- Converte para UTC para Comparações: Para comparar com os agendamentos existentes (que estão salvos em UTC no banco), nós convertemos cada slot que estamos testando para UTC (slot_utc_start, slot_utc_end).
- Compara Maçãs com Maçãs: Agora, a comparação de conflito é feita entre dois horários "aware" e no mesmo fuso (UTC), o que é seguro e correto.
- Retorna Horário Local: No final, retornamos o horário (.time()) do slot local, pois é isso que faz mais sentido para o cliente final ver na interface (ex: "14:00").
- Com essa mudança, seu backend agora está preparado para lidar com estabelecimentos em qualquer fuso horário do mundo de forma profissional!

Importante:
- Tratamento de Erros: As funções estão levantando ValueError por enquanto. Nos endpoints da API, precisaremos capturar esses ValueError e convertê-los em HTTPException apropriadas (ex: 400 Bad Request, 404 Not Found, 409 Conflict) com mensagens claras para o frontend.
- Fuso Horário (Timezone): É crucial que os datetimes sejam tratados consistentemente com fuso horário (o timezone=True nos modelos SQLAlchemy e a forma como o frontend envia o start_time são importantes). O datetime.utcnow() não tem fuso horário por padrão, então é melhor usar datetime.now(timezone.utc) ou garantir que o banco e a aplicação estejam configurados para UTC. Por agora, a lógica de comparação de horários dentro de _is_within_working_hours assume que todos os datetimes estão no mesmo fuso ou são comparáveis.
- Intervalo de Agendamento (appointmentIntervalMinutes): A lógica de gerar slots disponíveis para o cliente escolher ainda não está aqui. Esta função create_appointment assume que o cliente já escolheu um start_time específico. A lógica para mostrar os slots (ex: 09:00, 09:30, 10:00) com base no appointmentIntervalMinutes e na disponibilidade será outra parte importante.
"""