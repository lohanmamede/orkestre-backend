from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # Importaremos para relacionamentos futuros

from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com Estabelecimento
    establishment = relationship("Establishment", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # ... created_at, updated_at ...
    
    """ 
    - establishment: Relacionamento com o modelo Establishment, onde uselist=False indica que cada usuário tem no máximo um estabelecimento associado. 
    - cascade="all, delete-orphan" aqui significa que se o usuário for deletado, o estabelecimento associado também será
    """
    
    