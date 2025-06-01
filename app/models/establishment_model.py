from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Establishment(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    # working_hours_config = Column(JSON, nullable=True) # Para guardar config de horários

    user_id = Column(Integer, ForeignKey("users.id")) # Chave estrangeira para users.id
    # user = relationship("User", back_populates="establishment") # Relacionamento de volta para User

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relacionamento com Serviços (definiremos o Service depois)
    # services = relationship("Service", back_populates="establishment")