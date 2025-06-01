from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate, User as UserSchema # Renomeando User para UserSchema para evitar conflito com o modelo
from app.services import user_service # Nosso serviço de usuário
from app.api import deps # Nossa dependência get_db

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_new_user(
    *,
    db: Session = Depends(deps.get_db), # Injeta a sessão do banco
    user_in: UserCreate # Espera dados no formato UserCreate
):
    """
    Cria um novo usuário (e seu estabelecimento associado, futuramente).
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário com este email.",
        )

    new_user = user_service.create_user(db=db, user_in=user_in)
    # Aqui, futuramente, também criaríamos o Establishment associado ao new_user.id

    return new_user