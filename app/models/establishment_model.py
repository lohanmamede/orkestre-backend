## app/models/establishment_model.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.user_establishment_link import user_establishment_link

class Establishment(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String(20), nullable=True) # <<<--- CAMPO ADICIONADO DE VOLTA
    timezone = Column(String, default="America/Sao_Paulo", nullable=False)
    # Adicionando outros campos que planejamos para o "website"
    logo_url = Column(String, nullable=True)
    banner_image_url = Column(String, nullable=True)
    display_address = Column(String, nullable=True)
    about_text = Column(Text, nullable=True)
    social_links = Column(JSON, nullable=True)
    working_hours_config = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # REMOVIDO: a chave estrangeira 'user_id' e o relacionamento 'user'
    # ADICIONADO: o relacionamento muitos-para-muitos 'users'
    users = relationship(
        "User",
        secondary=user_establishment_link,
        back_populates="establishments"
    )

    # Relacionamentos 1:N
    services = relationship("Service", back_populates="establishment", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="establishment", cascade="all, delete-orphan")