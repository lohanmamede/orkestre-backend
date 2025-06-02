from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps # Nossa dependência get_db
from app.schemas.service_schema import Service, ServiceCreate, ServiceUpdate # Nossos schemas de serviço
from app.services import service_service # Nossos serviços CRUD para Service
# Para autenticação (vamos precisar em breve para proteger e verificar o dono)
# from app.services import user_service 
# from app.models.user_model import User 
# from app.core.security import get_current_active_user # Placeholder para a dependência do usuário atual

router = APIRouter()

@router.post("/establishments/{establishment_id}/services/", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service_for_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    service_in: ServiceCreate
    # current_user: User = Depends(get_current_active_user) # Adicionaremos para proteção
):
    """
    Cria um novo serviço para um estabelecimento específico.
    TODO: Adicionar verificação para garantir que current_user é o dono do establishment_id.
    """
    # Verifica se o estabelecimento existe
    establishment = service_service.check_establishment_exists(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    # TODO: Verificar se current_user.id == establishment.user_id

    service = service_service.create_establishment_service(db=db, service_in=service_in, establishment_id=establishment_id)
    return service

@router.get("/establishments/{establishment_id}/services/", response_model=List[Service])
def read_services_for_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    skip: int = 0,
    limit: int = 100
    # current_user: User = Depends(get_current_active_user) # Pode ser público ou protegido
):
    """
    Lista os serviços de um estabelecimento específico.
    """
    establishment = service_service.check_establishment_exists(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    services = service_service.get_services_by_establishment(db=db, establishment_id=establishment_id, skip=skip, limit=limit)
    return services

@router.get("/services/{service_id}", response_model=Service)
def read_service(
    *,
    db: Session = Depends(deps.get_db),
    service_id: int
    # current_user: User = Depends(get_current_active_user) # Para verificar se o usuário tem permissão para ver este serviço
):
    """
    Obtém um serviço específico pelo ID.
    """
    db_service = service_service.get_service(db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    # TODO: Adicionar verificação de permissão se este endpoint for protegido
    # Por exemplo, verificar se db_service.establishment.user_id == current_user.id

    return db_service

@router.put("/services/{service_id}", response_model=Service)
def update_existing_service(
    *,
    db: Session = Depends(deps.get_db),
    service_id: int,
    service_in: ServiceUpdate
    # current_user: User = Depends(get_current_active_user) # Essencial para proteção
):
    """
    Atualiza um serviço existente.
    TODO: Adicionar verificação para garantir que current_user é o dono do serviço (via estabelecimento).
    """
    db_service = service_service.get_service(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    # TODO: Verificar se current_user.id == db_service.establishment.user_id

    updated_service = service_service.update_service(db=db, service_db_obj=db_service, service_in=service_in)
    return updated_service

@router.delete("/services/{service_id}", response_model=Service) # Ou poderia retornar status 204 No Content
def delete_existing_service(
    *,
    db: Session = Depends(deps.get_db),
    service_id: int
    # current_user: User = Depends(get_current_active_user) # Essencial para proteção
):
    """
    Deleta um serviço existente.
    TODO: Adicionar verificação para garantir que current_user é o dono do serviço (via estabelecimento).
    """
    db_service = service_service.get_service(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    # TODO: Verificar se current_user.id == db_service.establishment.user_id

    deleted_service = service_service.delete_service(db=db, service_id=service_id)
    # Se delete_service retornar None é porque não foi encontrado, mas já checamos antes.
    # Se quisermos retornar 204, não retornamos corpo. Por ora, retornamos o objeto deletado.
    return deleted_service

"""
Explicação dos Endpoints e Pontos de Atenção (TODOs de Segurança):

create_service_for_establishment (POST /establishments/{establishment_id}/services/):
    - Cria um serviço vinculado a um establishment_id específico.
    - TODO Segurança: Precisamos garantir que o usuário logado (current_user) é o proprietário do establishment_id antes de permitir a criação.
read_services_for_establishment (GET /establishments/{establishment_id}/services/):
    - Lista os serviços de um estabelecimento. Pode ser um endpoint público (se a página de agendamento do estabelecimento for pública) ou protegido.
read_service (GET /services/{service_id}):
    - Obtém um serviço específico.
    - TODO Segurança: Se for protegido, verificar se o current_user tem permissão para ver este serviço.
update_existing_service (PUT /services/{service_id}):
    - Atualiza um serviço.
    - TODO Segurança: Essencial verificar se o current_user é o proprietário do serviço.
delete_existing_service (DELETE /services/{service_id}):
    - Deleta um serviço.
    - TODO Segurança: Essencial verificar se o current_user é o proprietário do serviço.

Placeholder get_current_active_user:
Por enquanto, comentei as linhas current_user: User = Depends(get_current_active_user). Esta será uma dependência que criaremos em breve (provavelmente no app/api/deps.py) que irá:

    1. Pegar o token JWT do cabeçalho da requisição.
    2. Decodificar e validar o token (usando uma função verify_token que adicionaremos ao app/core/security.py).
    3. Buscar o usuário correspondente no banco de dados.
    4. Retornar o objeto User do usuário logado. Com isso, poderemos fazer as verificações de propriedade mencionadas nos TODOs. Não se preocupe em implementar get_current_active_user AGORA. Vamos primeiro fazer os endpoints CRUD funcionarem, e depois adicionaremos a camada de proteção.
"""