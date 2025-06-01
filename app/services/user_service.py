from sqlalchemy.orm import Session
from passlib.context import CryptContext # Para hashear senhas

from app.models.user_model import User # Nosso modelo SQLAlchemy User
from app.schemas.user_schema import UserCreate # Nosso schema Pydantic para criação de usuário

# Configuração para o hashing de senhas
# Colocamos isso aqui, mas em projetos maiores poderia estar em um arquivo de core/security.py
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return PWD_CONTEXT.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha plana corresponde a um hash."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, *, email: str) -> User | None:
    """Busca um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    """Cria um novo usuário."""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password
        # is_active é True por padrão no modelo
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Para pegar o ID gerado pelo banco e outros defaults
    return db_user

# Futuramente:
# def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
#     user = get_user_by_email(db, email=email)
#     if not user:
#         return None
#     if not verify_password(password, user.hashed_password):
#         return None
#     return user

