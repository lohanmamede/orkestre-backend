from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta # Para definir um tempo de expiração customizado se necessário

# Nossos módulos
from app.schemas.user_schema import UserLogin, Token # Schemas para entrada de login e saída de token
from app.schemas.user_schema import User as UserSchema # Mantemos o alias para o response_model do registro. User as UserSchema evita conflito com o User do modelo SQLAlchemy 
from app.schemas.user_schema import UserCreate # Já estava aqui para o registro
from app.services import user_service # Nosso serviço de usuário
from app.api import deps # Nossa dependência get_db
from app.core import security # Nosso novo módulo de segurança
from app.core.config import settings # Para pegar o tempo de expiração do token

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

# Dentro de app/api/v1/endpoints/auth_router.py, abaixo do endpoint de registro

# Dentro de app/api/v1/endpoints/auth_router.py, abaixo do endpoint de registro

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: UserLogin = Depends() # FastAPI também pode injetar dependências de schemas no corpo
                                     # ou você pode usar: user_credentials: UserLogin
):
    """
    Autentica um usuário e retorna um token de acesso JWT.
    Para usar com 'application/json', envie email e password no corpo do request.
    """
    user = user_service.authenticate_user(
        db, email=form_data.email, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"}, # Padrão para erros de autenticação
        )

    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}