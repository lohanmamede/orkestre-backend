# app/services/status_validation_service.py
from datetime import datetime, timedelta, timezone
from app.models.appointment_model import Appointment, AppointmentStatus

# Matriz de transições que são IMPOSSÍVEIS e devem ser bloqueadas,
# atualizada para espelhar as regras do frontend
BLOCKED_TRANSITIONS = {
    AppointmentStatus.COMPLETED: [
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.CANCELLED_BY_CLIENT,
        AppointmentStatus.CANCELLED_BY_ESTABLISHMENT,
        AppointmentStatus.NO_SHOW,
        AppointmentStatus.RESCHEDULED,
    ],
    AppointmentStatus.CANCELLED_BY_CLIENT: [
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW,
        AppointmentStatus.CANCELLED_BY_ESTABLISHMENT
        # RESCHEDULED não está na lista - cancelados podem ser reagendados
    ],
    AppointmentStatus.CANCELLED_BY_ESTABLISHMENT: [
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW,
        AppointmentStatus.CANCELLED_BY_CLIENT
        # RESCHEDULED não está na lista - cancelados podem ser reagendados
    ],
    AppointmentStatus.NO_SHOW: [
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED_BY_CLIENT,
        AppointmentStatus.CANCELLED_BY_ESTABLISHMENT,
        AppointmentStatus.RESCHEDULED
    ],
    AppointmentStatus.RESCHEDULED: [
        AppointmentStatus.CONFIRMED,  # Reagendado não deve ter botão confirmar
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW
    ]
}

class StatusTransitionError(ValueError):
    """Exceção customizada para transições de status inválidas."""
    pass

def validate_status_transition(appointment: Appointment, new_status: AppointmentStatus):
    """
    Valida se uma mudança de status é permitida, incluindo regras de integridade e temporais.
    Espelha as validações do frontend para consistência.
    Levanta um StatusTransitionError se a transição for inválida.
    """
    current_status = appointment.status
    appointment_time = appointment.start_time
    now_utc = datetime.now(timezone.utc)
    is_appointment_passed = now_utc > appointment_time

    # Regra 1: Não pode transicionar para o mesmo status
    if current_status == new_status:
        raise StatusTransitionError("O agendamento já está com este status.")

    # REGRA TEMPORAL CRÍTICA (PRIORIDADE MÁXIMA) - igual ao frontend
    if is_appointment_passed:
        # Para agendamentos passados com status críticos, só permitir COMPLETED ou NO_SHOW
        if current_status in [AppointmentStatus.CONFIRMED, AppointmentStatus.RESCHEDULED, AppointmentStatus.PENDING]:
            if new_status not in [AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW]:
                raise StatusTransitionError("Agendamentos que já passaram do horário só podem ser marcados como 'Concluído' ou 'Não Compareceu'.")
        # Para outros status passados, aplicar matriz normal
        elif new_status in BLOCKED_TRANSITIONS.get(current_status, []):
            raise StatusTransitionError(f"A transição do status '{current_status.value}' para '{new_status.value}' não é permitida.")
    else:
        # Se não passou do horário, aplicar matriz de bloqueio normalmente
        if new_status in BLOCKED_TRANSITIONS.get(current_status, []):
            # Mensagens específicas para casos comuns
            if current_status == AppointmentStatus.COMPLETED:
                raise StatusTransitionError("Um agendamento concluído não pode ser alterado.")
            elif current_status in [AppointmentStatus.CANCELLED_BY_CLIENT, AppointmentStatus.CANCELLED_BY_ESTABLISHMENT] and new_status == AppointmentStatus.COMPLETED:
                raise StatusTransitionError("Um agendamento cancelado não pode ser marcado como concluído.")
            elif current_status in [AppointmentStatus.CANCELLED_BY_CLIENT, AppointmentStatus.CANCELLED_BY_ESTABLISHMENT] and new_status == AppointmentStatus.NO_SHOW:
                raise StatusTransitionError("Um agendamento cancelado não pode ser marcado como não-comparecimento.")
            elif current_status == AppointmentStatus.NO_SHOW and new_status in [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]:
                raise StatusTransitionError("Um agendamento com não-comparecimento não pode voltar a ser confirmado.")
            else:
                raise StatusTransitionError(f"A transição do status '{current_status.value}' para '{new_status.value}' não é permitida.")

    # Regra 3: Validações temporais específicas
    if new_status == AppointmentStatus.COMPLETED and now_utc < appointment_time:
        raise StatusTransitionError("Só é possível marcar como concluído após o horário de início.")

    if new_status == AppointmentStatus.IN_PROGRESS:
        thirty_minutes_before = appointment_time - timedelta(minutes=30)
        if now_utc < thirty_minutes_before:
            raise StatusTransitionError("Só é possível iniciar um atendimento 30 minutos antes do horário agendado.")
        if now_utc > appointment_time:
            raise StatusTransitionError("Muito tarde para iniciar o atendimento. Use a opção de completar diretamente.")

    if new_status == AppointmentStatus.NO_SHOW:
        # Para agendamentos críticos passados, não aplicar restrição temporal
        is_critical_past = is_appointment_passed and current_status in [AppointmentStatus.CONFIRMED, AppointmentStatus.RESCHEDULED, AppointmentStatus.PENDING]
        if not is_critical_past and now_utc < appointment_time:
            raise StatusTransitionError("Só é possível marcar não-comparecimento após o horário agendado.")

    return True