# app/models/professional_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Professional(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    establishment_id = Column(Integer, ForeignKey("establishments.id"), nullable=False)

    establishment = relationship("Establishment")