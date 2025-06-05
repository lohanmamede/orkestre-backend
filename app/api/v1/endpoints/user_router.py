from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session # Se precisar de acesso direto ao db, mas get_current_active_user já faz

from app.api import deps
from app.models.user_model import User # Para o tipo do current_user
from app.schemas.user_schema import UserMe # Nosso novo schema de resposta

router = APIRouter()

@router.get("/me", response_model=UserMe)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user) # Usa nossa dependência
):
    """
    Obtém o perfil do usuário logado atualmente, incluindo seu estabelecimento.
    """
    # O objeto current_user já vem com o relacionamento 'establishment'
    # carregado (ou acessível via lazy loading) devido à configuração do SQLAlchemy.
    # O Pydantic (com from_attributes=True) vai conseguir mapear user.establishment para o schema EstablishmentForUserMe.
    return current_user

"""
- @router.get("/me", response_model=UserMe): Define o endpoint.
- current_user: User = Depends(deps.get_current_active_user): Nossa dependência mágica que nos dá o objeto User do usuário logado e ativo.
- return current_user: O Pydantic, através do response_model=UserMe e from_attributes=True (que deve estar no BaseSchema de UserMe), fará o trabalho de pegar os dados do objeto current_user (incluindo current_user.establishment se o relacionamento estiver configurado e o EstablishmentForUserMe schema estiver correto) e montar a resposta no formato UserMe.
"""