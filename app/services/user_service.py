# Este arquivo contém a lógica de negócios relacionada aos estabelecimentos.
# Ele interage com o banco de dados e aplica regras de negócio específicas.
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from passlib.context import CryptContext # Para hashear senhas

from app.models.user_model import User # Nosso modelo SQLAlchemy User
from app.schemas.user_schema import UserCreate # Nosso schema Pydantic para criação de usuário

from app.models.establishment_model import Establishment # Importe o modelo Establishment
from app.services import establishment_service # Se precisarmos de alguma função auxiliar dele

from app.models.role_enum import Role


# Configuração para o hashing de senhas
# Colocamos isso aqui, mas em projetos maiores poderia estar em um arquivo de core/security.py
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return PWD_CONTEXT.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha plana corresponde a um hash."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, *, email: str) -> Optional[User]:
    """Busca um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, *, user_id: int) -> Optional[User]:
    """Busca um usuário pelo seu ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    print("\n--- [INÍCIO] Tentando criar usuário... ---")
    try:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        print("--- [PONTO 1] Objeto User criado em memória.")

        if user_in.establishment_name:
            print("--- [PONTO 2a] Entrando no fluxo de criação de Estabelecimento.")
            db_establishment = Establishment(name=user_in.establishment_name)
            db_user.establishments.append(db_establishment)
            db.add(db_establishment)

            print(f"--- [PONTO 3a] Objetos prontos para o commit inicial.")
            db.commit()
            print("--- [PONTO 4a] Primeiro commit (User e Estab) bem-sucedido.")
            db.refresh(db_user)
            db.refresh(db_establishment)
            print("--- [PONTO 5a] Refresh de User e Estab bem-sucedido.")

            from app.models.user_establishment_link import user_establishment_link
            from app.models.role_enum import Role
            update_stmt = (
                user_establishment_link.update().
                where(user_establishment_link.c.user_id == db_user.id).
                where(user_establishment_link.c.establishment_id == db_establishment.id).
                values(role=Role.OWNER)
            )
            db.execute(update_stmt)
            print("--- [PONTO 6a] Declaração de update para OWNER executada.")
            db.commit()
            print("--- [PONTO 7a] Segundo commit (role) bem-sucedido.")

        else:
            print("--- [PONTO 2b] Entrando no fluxo de criação de User-Apenas.")
            db.commit()
            print("--- [PONTO 3b] Commit do User-Apenas bem-sucedido.")
            db.refresh(db_user)
            print("--- [PONTO 4b] Refresh do User-Apenas bem-sucedido.")

        print("--- [PONTO 8] Buscando usuário final com relacionamentos...")
        final_user = db.query(User).options(
            joinedload(User.establishments)
        ).filter(User.id == db_user.id).first()

        if not final_user:
            print("--- [ERRO] Usuário final não encontrado após a criação!")
            raise ValueError("Não foi possível recuperar o usuário após a criação.")

        print(f"--- [PONTO 9] Retornando final_user (ID: {final_user.id}) com {len(final_user.establishments)} estabelecimento(s).")
        return final_user

    except Exception as e:
        print(f"\n!!!!!!!!!! ERRO INESPERADO DENTRO DE CREATE_USER !!!!!!!!!!")
        print(f"TIPO DO ERRO: {type(e)}")
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise e

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