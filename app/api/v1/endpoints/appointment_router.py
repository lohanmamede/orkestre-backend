from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time # Para os filtros de data

from app.api import deps
from app.models.user_model import User
from app.schemas.appointment_schema import Appointment as AppointmentSchema, AppointmentCreate, AppointmentStatus, AppointmentStatusUpdate # Nossos schemas
from app.services import appointment_service, establishment_service # Nossos serviços

# Importa o modelo AppointmentModel para evitar conflito de nome com o schema Appointment
from app.models.appointment_model import Appointment as AppointmentModel

from app.services import status_validation_service # Novo import
from app.services.status_validation_service import StatusTransitionError # Importa a exceção customizada

router = APIRouter()

@router.post("/establishments/{establishment_id}/appointments/", response_model=AppointmentSchema, status_code=status.HTTP_201_CREATED)
def create_new_appointment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    appointment_in: AppointmentCreate,
    # current_user: User = Depends(deps.get_current_active_user) # Cliente final pode não estar logado para agendar.
                                                                # A lógica de quem pode agendar precisa ser definida.
                                                                # Por agora, vamos focar na funcionalidade.
):
    """
    Cria um novo agendamento para um estabelecimento.
    Este endpoint pode ser público para clientes ou protegido para o profissional agendar para um cliente.
    """
    # Verifica se o estabelecimento existe
    db_establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not db_establishment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    try:
        appointment = appointment_service.create_appointment(
            db=db, appointment_in=appointment_in, establishment_id=establishment_id
        )
        return appointment
    except ValueError as e: # Captura os ValueErrors que levantamos no service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Captura outros erros inesperados
        # Logar o erro e retornar um erro genérico é uma boa prática
        # logger.error(f"Erro inesperado ao criar agendamento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocorreu um erro ao processar sua solicitação.")


@router.get("/establishments/{establishment_id}/appointments/", response_model=List[AppointmentSchema])
def list_appointments_for_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status_filter: Optional[AppointmentStatus] = None, # Renomeado de 'status' para 'status_filter' para evitar conflito
    current_user: User = Depends(deps.get_current_active_user) # Profissional precisa estar logado para ver sua agenda
):
    """
    Lista os agendamentos de um estabelecimento específico.
    Apenas o proprietário do estabelecimento pode ver esta lista.
    """
    db_establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not db_establishment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    # Verificação de propriedade
    if db_establishment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Não tem permissão para ver os agendamentos deste estabelecimento"
        )

    appointments = appointment_service.get_appointments_by_establishment(
        db=db, 
        establishment_id=establishment_id, 
        skip=skip, 
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        status=status_filter # Passa o status_filter para a função de serviço
    )
    return appointments

# Endpoints para GET específico, PUT (atualizar status), DELETE virão aqui...
@router.get("/appointments/{appointment_id}", response_model=AppointmentSchema)
def read_specific_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Obtém um agendamento específico pelo ID.
    Apenas o proprietário do estabelecimento ao qual o agendamento pertence pode vê-lo.
    """
    # Primeiro, buscamos o agendamento sem verificar o estabelecimento
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first() # Usando AppointmentModel para evitar conflito de nome

    if not db_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    # Agora verificamos a propriedade através do establishment_id no agendamento
    # Esta abordagem requer que o objeto Establishment seja carregado ou que user_id esteja no Establishment
    # Se db_appointment.establishment.user_id não funcionar diretamente por causa de lazy loading,
    # podemos buscar o estabelecimento primeiro.
    # Mas como temos establishment_id no appointment, podemos buscar o establishment.

    db_establishment = establishment_service.get_establishment_by_id(db, establishment_id=db_appointment.establishment_id)

    if not db_establishment or db_establishment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Não tem permissão para ver este agendamento"
        )
    return db_appointment

@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentSchema)
def update_appointment_status_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    status_update: AppointmentStatusUpdate, # Recebe o novo status no corpo
    current_user: User = Depends(deps.get_current_active_user) # Garante que o usuário está autenticado
):
    """
    Atualiza o status de um agendamento, com validação de regras de negócio.
    Apenas o proprietário do estabelecimento pode realizar esta ação.
    """
    # 1. Busca o agendamento no banco de dados
    db_appointment = appointment_service.get_appointment(db, appointment_id=appointment_id)
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Agendamento não encontrado"
        )

    # 2. Verifica a propriedade (Autorização)
    # Garante que o usuário logado é o dono do estabelecimento ao qual o agendamento pertence.
    if db_appointment.establishment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem permissão para modificar este agendamento"
        )
    
    # 3. Valida a transição de status (Regras de Negócio)
    # Chama nosso novo serviço de validação antes de qualquer alteração.
    try:
        # CORRETO:
        status_validation_service.validate_status_transition( 
            appointment=db_appointment, 
            new_status=status_update.status
        )
    except StatusTransitionError as e:
        # Se o serviço de validação levantar um erro de regra, retorna um erro 400.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 4. Se todas as validações e autorizações passaram, atualiza o status
    updated_appointment = appointment_service.update_appointment_status(
        db=db, 
        appointment_db_obj=db_appointment, 
        status_in=status_update.status
    )
    
    return updated_appointment

@router.get("/establishments/{establishment_id}/services/{service_id}/available-slots", response_model=List[time])
def get_available_appointment_slots(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    service_id: int,
    appointment_date: date # Recebe a data como parâmetro de query (ex: ?date=2025-06-10)
):
    """
    Retorna uma lista de horários de início disponíveis para um serviço em uma data específica.
    """
    try:
        available_slots = appointment_service.get_available_slots(
            db=db,
            establishment_id=establishment_id,
            service_id=service_id,
            appointment_date=appointment_date
        )
        return available_slots
    except Exception as e:
        # Este erro pode acontecer se, por exemplo, o serviço não pertence ao estabelecimento
        # A lógica no serviço já pode levantar um ValueError.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

"""
Explicação dos Endpoints:

- create_new_appointment (POST /establishments/{establishment_id}/appointments/):
    - Este é o endpoint que o cliente final usará para criar um agendamento.
    - Recebe o establishment_id no path e os dados do agendamento (AppointmentCreate) no corpo.
    - Autenticação: Eu comentei a linha current_user: User = Depends(deps.get_current_active_user). Precisamos decidir se um cliente precisa estar logado para agendar. Para um MVP focado na facilidade do cliente final, talvez ele não precise de login no sistema do profissional. Se for o caso, este endpoint seria público (mas o backend ainda precisa garantir que o establishment_id é válido e que o service_id pertence a ele). Se exigirmos login do cliente, descomentaremos e ajustaremos. Por agora, vamos assumir que é público para o cliente final, mas o create_appointment no serviço já faz validações importantes.
    - Tratamento de Erro: Ele captura ValueError que nosso appointment_service.create_appointment pode levantar (ex: "Horário ocupado", "Fora do expediente") e os converte em HTTPException 400 Bad Request com a mensagem de erro. Também tem um catch genérico para outros erros.
- list_appointments_for_establishment (GET /establishments/{establishment_id}/appointments/):
    - Este endpoint é para o profissional (dono do estabelecimento) ver sua agenda.
    - Ele é protegido (current_user: User = Depends(deps.get_current_active_user)).
    - Ele verifica a propriedade: Garante que o current_user é o dono do establishment_id.
    - Permite filtros por start_date, end_date e status (renomeei o parâmetro para status_filter para evitar conflito com o status do FastAPI).
    - Chama o appointment_service.get_appointments_by_establishment.
"""