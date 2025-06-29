# Este arquivo é um router para estabelecimentos, ou seja, ele define endpoints relacionados a estabelecimentos e suas configurações de horários de atendimento.
# Ele usa o FastAPI para definir rotas e o SQLAlchemy para interagir com o banco de dados.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List # Para o tipo de retorno do PUT
from app.schemas.establishment_schema import MemberSchema

from app.api import deps
from app.models.user_model import User # Para o current_user
from app.models.establishment_model import Establishment # Para type hint
from app.schemas.establishment_schema import Establishment as EstablishmentSchema # Para o GET
from app.schemas.working_hours_schema import WorkingHoursConfig # Para o corpo do PUT
from app.schemas.establishment_schema import CollaboratorCreate
from app.services import establishment_service, user_service

from app.models.role_enum import Role # Importe o Role
from app.models.user_establishment_link import user_establishment_link

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
    response_data = establishment_service.get_establishment_for_api_response(
        db=db,
        establishment_id=establishment.id
    )
    return response_data

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
    
# --- Endpoint para Adicionar Colaboradores ---
@router.post("/{establishment_id}/collaborators", response_model=EstablishmentSchema)
def add_collaborator_to_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    collaborator_in: CollaboratorCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Adiciona um usuário como colaborador a um estabelecimento.
    Apenas o OWNER do estabelecimento pode fazer isso.
    """
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")

    # Lógica de Autorização para verificar se o usuário logado é um OWNER
    link = db.query(user_establishment_link).filter_by(
        user_id=current_user.id,
        establishment_id=establishment.id
    ).first()

    if not link or link.role != Role.OWNER:
        raise HTTPException(status_code=403, detail="Apenas o proprietário pode adicionar colaboradores.")

    try:
        # 1. Executa a lógica de negócio para adicionar o colaborador
        establishment_service.add_collaborator(
            db=db,
            establishment=establishment,
            collaborator_email=collaborator_in.email
        )
        
        # 2. Após a escrita, usa a nova função para buscar e montar a resposta completa
        response_data = establishment_service.get_establishment_for_api_response(
            db=db,
            establishment_id=establishment.id
        )
        if not response_data:
            # Isso não deveria acontecer se a lógica acima funcionou, mas é uma boa checagem
            raise HTTPException(status_code=404, detail="Estabelecimento não encontrado após a atualização.")
            
        return response_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{establishment_id}/members", response_model=List[MemberSchema])
def list_establishment_members(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Lista todos os membros (donos e colaboradores) de um estabelecimento.
    Apenas membros do estabelecimento podem ver a lista.
    """
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")

    # Autorização: Verifica se o usuário logado é um membro deste estabelecimento
    is_member = any(user.id == current_user.id for user in establishment.users)
    if not is_member:
        raise HTTPException(status_code=403, detail="Você não tem permissão para ver os membros deste estabelecimento.")

    # Usa a função que já temos para montar a resposta com os papéis corretos
    response_data = establishment_service.get_establishment_for_api_response(
        db=db,
        establishment_id=establishment.id
    )
    return response_data.users

@router.delete("/{establishment_id}/members/{user_id_to_remove}", response_model=EstablishmentSchema)
def remove_collaborator_from_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    user_id_to_remove: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Remove um membro (colaborador ou outro dono) de um estabelecimento.
    Apenas o OWNER do estabelecimento pode fazer isso.
    """
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")

    # Autorização: Verifica se o usuário logado é um OWNER
    owner_link = db.query(user_establishment_link).filter_by(user_id=current_user.id, establishment_id=establishment.id).first()
    if not owner_link or owner_link.role != Role.OWNER:
        raise HTTPException(status_code=403, detail="Apenas o proprietário pode remover membros.")

    # Busca o usuário a ser removido
    collaborator_to_remove = user_service.get_user_by_id(db, user_id=user_id_to_remove)
    if not collaborator_to_remove:
        raise HTTPException(status_code=404, detail="Usuário a ser removido não encontrado.")

    try:
        establishment_service.remove_collaborator(
            db=db,
            establishment=establishment,
            collaborator_to_remove=collaborator_to_remove
        )

        # Retorna o estado atualizado do estabelecimento com a lista de membros
        response_data = establishment_service.get_establishment_for_api_response(
            db=db,
            establishment_id=establishment.id
        )
        return response_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))