# Este arquivo contém a lógica de negócios relacionada aos estabelecimentos.
# Ele interage com o banco de dados e aplica regras de negócio específicas.
from sqlalchemy.orm import Session
from passlib.context import CryptContext # Para hashear senhas

from app.models.user_model import User # Nosso modelo SQLAlchemy User
from app.schemas.user_schema import UserCreate # Nosso schema Pydantic para criação de usuário

from app.models.establishment_model import Establishment # Importe o modelo Establishment
from app.services import establishment_service # Se precisarmos de alguma função auxiliar dele

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
    """
    Cria um novo usuário e seu estabelecimento associado.
    """
    hashed_password = get_password_hash(user_in.password)

    # 1. Cria o objeto User
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit() # Faz o commit para que o ID do usuário seja gerado pelo banco
    db.refresh(db_user) # Atualiza o objeto db_user com os dados do banco (incluindo o ID)

    # 2. Cria o objeto Establishment associado
    if user_in.establishment_name:
        db_establishment = Establishment(
            name=user_in.establishment_name,
            user_id=db_user.id # Associa ao usuário recém-criado
        )
        db.add(db_establishment)
        db.commit()
        db.refresh(db_establishment)

    return db_user

def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    """
    Autentica um usuário. Retorna o usuário se as credenciais forem válidas, senão None.
    """
    user = get_user_by_email(db, email=email) # Reutiliza a função que já temos
    if not user:
        return None # Usuário não encontrado
    if not user.is_active: # Opcional: Verificar se o usuário está ativo
        return None # Ou poderia levantar uma exceção específica para usuário inativo
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None # Senha incorreta
    return user # Sucesso! Usuário e senha corretos