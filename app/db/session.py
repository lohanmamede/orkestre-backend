from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para criar tabelas (chamar isso no main.py para desenvolvimento)
def init_db():
    from app.db.base_class import Base
    # Importar todos os modelos aqui para que sejam registrados no Base
    from app.models.user_model import User
    from app.models.establishment_model import Establishment
    from app.models.service_model import Service

    Base.metadata.create_all(bind=engine)