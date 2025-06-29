# app/models/user_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.user_establishment_link import user_establishment_link

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    is_email_verified = Column(Boolean(), default=False) # Para a futura verificação de email

    # REMOVIDO: o relacionamento um-para-um 'establishment'
    # ADICIONADO: o relacionamento muitos-para-muitos 'establishments'
    establishments = relationship(
        "Establishment",
        secondary=user_establishment_link,
        back_populates="users"
    )