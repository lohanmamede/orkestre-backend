# Este arquivo é um router para estabelecimentos, ou seja, ele define endpoints relacionados a estabelecimentos e suas configurações de horários de atendimento.
# Ele usa o FastAPI para definir rotas e o SQLAlchemy para interagir com o banco de dados.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any # Para o tipo de retorno do PUT

from app.api import deps
from app.models.user_model import User # Para o current_user
from app.models.establishment_model import Establishment # Para type hint
from app.schemas.establishment_schema import Establishment as EstablishmentSchema # Para o GET
from app.schemas.working_hours_schema import WorkingHoursConfig # Para o corpo do PUT
from app.services import establishment_service # Nosso novo serviço

router = APIRouter()

@router.put("/{establishment_id}/working-hours", response_model=EstablishmentSchema)
def set_establishment_working_hours(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    working_hours_in: WorkingHoursConfig, # Recebe a configuração no corpo da requisição
    current_user: User = Depends(deps.get_current_active_user) # Protegido
):
    """
    Define ou atualiza a configuração de horários de atendimento para um estabelecimento.
    """
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Estabelecimento não encontrado"
        )
    
    # Verificação de propriedade
    if establishment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Não tem permissão para configurar os horários deste estabelecimento"
        )
    
    updated_establishment = establishment_service.update_establishment_working_hours(
        db=db, 
        establishment_db_obj=establishment, 
        working_hours_in=working_hours_in
    )
    return updated_establishment # Retorna o estabelecimento completo com os horários atualizados

@router.get("/{establishment_id}", response_model=EstablishmentSchema)
def read_establishment_details(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int
    # current_user: User = Depends(deps.get_current_active_user) # Decida se este GET é protegido ou público
):
    """
    Obtém os detalhes de um estabelecimento, incluindo seus horários de atendimento.
    """
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )
    # Se protegido, adicionar verificação de propriedade aqui
    return establishment

    """
    * **Endpoint `PUT /{establishment_id}/working-hours`**:
        * É um `PUT` porque geralmente a configuração de horários é definida como um todo (substituindo a configuração anterior, se houver). Poderia ser `PATCH` se permitíssemos atualizações parciais, mas `PUT` para o objeto completo de configuração é mais simples para começar.
        * Recebe o `establishment_id` no path e o objeto `WorkingHoursConfig` no corpo da requisição.
        * É protegido: apenas o `current_user` que for dono do estabelecimento pode alterá-lo.
        * Chama o `establishment_service.update_establishment_working_hours`.
        * Retorna o objeto `Establishment` completo (que agora incluirá o `working_hours_config` atualizado, pois o schema `EstablishmentSchema` já foi atualizado para incluí-lo).
    * **Endpoint `GET /{establishment_id}`**:
        * Adicionei este endpoint aqui como exemplo de onde você buscaria os detalhes do estabelecimento, incluindo a configuração de horários (se ela existir no banco).
        * Você precisa decidir se este endpoint será público ou protegido (assim como discutimos para os serviços). Se for para a página pública de agendamento precisar desses horários, ele talvez precise ser público ou ter uma versão pública. Por enquanto, deixei a proteção comentada.
    """