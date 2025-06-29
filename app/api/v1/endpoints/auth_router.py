# # Este arquivo é um router para a autenticação de usuários, incluindo registro e login.
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
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
):
    """
    Cria um novo usuário.
    O payload determina se ele cria um novo estabelecimento ou se junta a um existente.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário com este email.",
        )

    # --- BLOCO TRY...EXCEPT ADICIONADO AQUI ---
    try:
        new_user = user_service.create_user(db=db, user_in=user_in)
        # Futuramente, aqui também poderíamos enfileirar o e-mail de boas-vindas/verificação
        return new_user
    except ValueError as e:
        # Captura os erros de lógica de negócio do nosso serviço
        # (ex: "Código de convite inválido")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        # Captura qualquer outro erro inesperado para evitar um 500
        # Em produção, logaríamos este erro detalhadamente
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao processar o registro."
        )


@router.post("/login", response_model=Token)
async def login_for_access_token( # Adicionei async, é uma boa prática para I/O com banco
    login_credentials: UserLogin, # <--- ALTERAÇÃO PRINCIPAL AQUI
    db: Session = Depends(deps.get_db)
):
    """
    Autentica um usuário e retorna um token de acesso JWT.
    Espera email e password no corpo da requisição JSON.
    """
    user = user_service.authenticate_user(
        db, email=login_credentials.email, password=login_credentials.password # Use login_credentials aqui
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# {
#  "email": "teste1@example.com",
#  "password": "teste1"
# }