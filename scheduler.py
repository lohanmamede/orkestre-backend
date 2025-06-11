# scheduler.py (Versão Final Simplificada Síncrona)
import time
import pytz
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
# Importamos a função da tarefa DIRETAMENTE
from app.tasks import send_whatsapp_reminder
# Importamos os modelos necessários para a query
from app.models.appointment_model import Appointment, AppointmentStatus

# scheduler precisa conhecer os modelos do programa
from app.models.user_model import User
from app.models.establishment_model import Establishment
from app.models.service_model import Service

def schedule_and_send_reminders():
    """
    Busca por agendamentos que precisam de lembrete e CHAMA a função de envio diretamente.
    """
    print(f"[{datetime.now()}] Verificando agendamentos para enviar lembretes...")
    db: Session = SessionLocal()
    try:
        # A lógica de busca continua a mesma
        now_utc = datetime.now(timezone.utc)
        reminder_horizon = now_utc + timedelta(hours=24)

        appointments_to_remind = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.CONFIRMED,
            Appointment.reminder_sent_at == None,
            Appointment.start_time <= reminder_horizon,
            Appointment.start_time > now_utc
        ).all()

        if not appointments_to_remind:
            print("Nenhum agendamento para lembrar no momento.")
            return

        print(f"Encontrados {len(appointments_to_remind)} agendamentos para lembrar.")
        for appt in appointments_to_remind:
            try:
                print(f"Processando lembrete para o agendamento ID: {appt.id}...")

                # --- MUDANÇA PRINCIPAL: CHAMA A FUNÇÃO DIRETAMENTE ---
                send_whatsapp_reminder(appt.id) 

                # Se o envio foi bem-sucedido (não levantou exceção), marcamos no banco
                appt.reminder_sent_at = datetime.now(timezone.utc)
                db.add(appt)
                print(f"Lembrete para agendamento {appt.id} processado e marcado como enviado.")
            except Exception as e:
                # Se o envio para um agendamento falhar, logamos o erro e continuamos para o próximo
                print(f"ERRO ao processar lembrete para agendamento {appt.id}: {e}")

        db.commit() # Salva todas as alterações de reminder_sent_at no final
        print("Ciclo de lembretes finalizado.")

    except Exception as e:
        print(f"ERRO GERAL no scheduler: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    while True:
        schedule_and_send_reminders()
        sleep_interval = 600 # 10 minutos
        print(f"Agendador dormindo por {sleep_interval / 60} minutos...")
        time.sleep(sleep_interval)