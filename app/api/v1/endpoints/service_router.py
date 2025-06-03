# Este arquivo é um router para serviços, ou seja, ele define endpoints relacionados a serviços de um estabelecimento.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.user_model import User # Importe o modelo User
from app.api import deps # Nossa dependência get_db
from app.schemas.service_schema import Service, ServiceCreate, ServiceUpdate # Nossos schemas de serviço
from app.services import service_service # Nossos serviços CRUD para Service
# Para autenticação (vamos precisar em breve para proteger e verificar o dono)
# from app.services import user_service 
# from app.core.security import get_current_active_user # Placeholder para a dependência do usuário atual

router = APIRouter()

@router.post("/establishments/{establishment_id}/services/", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service_for_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    service_in: ServiceCreate,
    current_user: User = Depends(deps.get_current_active_user) # Usuário autenticado
):
    
    # Verifica se o estabelecimento existe
    establishment = service_service.check_establishment_exists(db, establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    # VERIFICAÇÃO DE PROPRIEDADE
    if establishment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para adicionar serviços a este estabelecimento")

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
    service_in: ServiceUpdate,
    current_user: User = Depends(deps.get_current_active_user) # Usuário autenticado
):
    db_service = service_service.get_service(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    # VERIFICAÇÃO DE PROPRIEDADE
    # Precisamos acessar service.establishment.user_id. O relacionamento deve estar carregado.
    # Se o relacionamento 'establishment' no modelo 'Service' estiver configurado corretamente, isso deve funcionar.
    if db_service.establishment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para atualizar este serviço")

    updated_service = service_service.update_service(db=db, service_db_obj=db_service, service_in=service_in)
    return updated_service

@router.delete("/services/{service_id}", response_model=Service)
def delete_existing_service(
    *,
    db: Session = Depends(deps.get_db),
    service_id: int,
    current_user: User = Depends(deps.get_current_active_user) # Usuário autenticado
):
    db_service = service_service.get_service(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    # VERIFICAÇÃO DE PROPRIEDADE
    if db_service.establishment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para deletar este serviço")

    deleted_service = service_service.delete_service(db=db, service_id=service_id)
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

""" Atualização dos TODOs

Explicação das Mudanças de Segurança:
    - current_user: User = Depends(deps.get_current_active_user): Adicionamos esta dependência aos endpoints que queremos proteger (criar, atualizar, deletar). O FastAPI executará get_current_active_user primeiro. Se o usuário não estiver autenticado ou não estiver ativo, um erro HTTP 401 ou 400 será levantado automaticamente, e o código do nosso endpoint nem será executado.

Verificação de Propriedade:
    - Para create_service_for_establishment: Verificamos se establishment.user_id (do estabelecimento encontrado no banco) é igual ao current_user.id.
    - Para update_existing_service e delete_existing_service: Buscamos o serviço (db_service). Acessamos db_service.establishment.user_id (graças ao relacionamento SQLAlchemy que configuramos) e comparamos com current_user.id.
    - Se a verificação de propriedade falhar, levantamos um HTTPException com status 403 Forbidden.

Endpoints de Leitura (GET): Eu deixei comentada a dependência current_user e a verificação de propriedade. Você precisa decidir:
    - Os serviços de um estabelecimento devem ser públicos (qualquer um pode ver, mesmo sem login)?
    - Ou apenas o dono do estabelecimento pode ver seus próprios serviços?
    - Ou qualquer usuário logado pode ver os serviços de qualquer estabelecimento?
    - Para o MVP, e para simplificar a página pública de agendamento no futuro, talvez faça sentido que read_services_for_establishment e read_service sejam públicos (não precisem de current_user). Mas se você quiser proteger tudo, é só descomentar e ajustar a lógica.
    
    Deixar público: Essencial para a Página Pública de Agendamento: Se queremos que os clientes finais dos Pet Shops/Clínicas possam ver os serviços disponíveis para agendar (o que é o core da nossa aplicação), esses dados precisam ser acessíveis publicamente. O frontend que renderizará a página de agendamento de um estabelecimento precisará buscar esses serviços sem exigir que o cliente final faça login como administrador.
"""