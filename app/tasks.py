# app/tasks.py
import os
import re
import pytz
import time # Precisaremos do 'time' para uma pequena pausa
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.db.session import SessionLocal
from app.models.appointment_model import Appointment
from app.core.config import settings

# --- Bloco de Inicialização do Cliente Twilio ---
if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

# --- Função Principal da Tarefa ---
def send_whatsapp_reminder(appointment_id: int):
    if not twilio_client:
        print("ERRO: Credenciais do Twilio não configuradas.")
        return "Falha: credenciais Twilio ausentes."

    print(f"--- TAREFA INICIADA PARA AGENDAMENTO ID: {appointment_id} ---")
    db: Session = SessionLocal()
    try:
        # 1. Busca os dados do agendamento
        appointment = db.query(Appointment).options(
            joinedload(Appointment.service),
            joinedload(Appointment.establishment)
        ).filter(Appointment.id == appointment_id).first()

        if not appointment:
            print(f"ERRO: Agendamento {appointment_id} não encontrado.")
            return

        # 2. Formata a mensagem
        customer_name = appointment.customer_name.split(' ')[0]
        # ... (resto da formatação da mensagem como antes)
        body_message = f"Lembrete Orkestre Agenda: seu agendamento para '{appointment.service.name}' está confirmado." # Mensagem simples para teste de template

        # 3. Prepara os números
        from_whatsapp_number = f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}'
        clean_phone = re.sub(r'\D', '', appointment.customer_phone)
        if not clean_phone.startswith('55'):
            clean_phone = f'55{clean_phone}'

        # Formato principal (com o 9, o mais comum)
        to_whatsapp_number_v1 = f'whatsapp:+{clean_phone}'

        # Formato alternativo (sem o 9)
        phone_without_9 = None
        if len(clean_phone) == 13 and clean_phone[4] == '9':
            phone_without_9 = clean_phone[:4] + clean_phone[5:]
            to_whatsapp_number_v2 = f'whatsapp:+{phone_without_9}'

        # 4. Tenta enviar e VERIFICA o status
        print(f"Tentando enviar para {to_whatsapp_number_v1}...")
        message_to_check = twilio_client.messages.create(
            from_=from_whatsapp_number,
            body=body_message,
            to=to_whatsapp_number_v1
        )

        # Espera um ou dois segundos para o status do Twilio ser atualizado
        time.sleep(2) 

        # Pega o status da mensagem que acabamos de tentar enviar
        message_status = twilio_client.messages(message_to_check.sid).fetch()

        # Se o status for 'failed' ou 'undelivered' com o erro de número inválido...
        if message_status.status == 'failed' and message_status.error_code in [63013, 63015]:
            print(f"Tentativa 1 falhou com erro de número inválido (Código: {message_status.error_code}). Tentando formato alternativo.")

            # Se tivermos um formato alternativo (sem o 9), tentamos
            if to_whatsapp_number_v2:
                print(f"Tentativa 2: Enviando para {to_whatsapp_number_v2}...")
                final_message = twilio_client.messages.create(
                    from_=from_whatsapp_number,
                    body=body_message,
                    to=to_whatsapp_number_v2
                )
                print(f"Mensagem enviada com sucesso na segunda tentativa! SID: {final_message.sid}")
            else:
                # Se não há formato alternativo, simplesmente falhamos
                raise TwilioRestException(status=message_status.status, uri='', msg=message_status.error_message, code=message_status.error_code)

        elif message_status.status in ['queued', 'sending', 'sent']:
             print(f"Mensagem enviada com sucesso na primeira tentativa! SID: {message_status.sid}, Status: {message_status.status}")
        else:
             # Se falhou por outro motivo
             raise TwilioRestException(status=message_status.status, uri='', msg=message_status.error_message, code=message_status.error_code)


        return f"Lembrete para o agendamento {appointment_id} processado."

    except Exception as e:
        print(f"FALHA AO PROCESSAR TAREFA para o agendamento {appointment_id}: {e}")
        raise e
    finally:
        db.close()