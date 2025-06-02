from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base # Importe a classe Base

class Service(Base):
    # __tablename__ será 'services' por causa da nossa Base

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True) # Usando Text para descrições potencialmente mais longas
    price = Column(Float, nullable=False) # Preço do serviço. Decidimos que seria informativo, mas precisa ser guardado.
    duration_minutes = Column(Integer, nullable=False) # Duração do serviço em minutos
    is_active = Column(Boolean(), default=True) # Para o profissional poder ativar/desativar um serviço

    establishment_id = Column(Integer, ForeignKey("establishments.id"), nullable=False)

    # Relacionamento de volta para Establishment
    establishment = relationship("Establishment", back_populates="services")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    """
    Estes relacionamentos permitirão que, por exemplo, a partir de um objeto Service, acessemos service.establishment.user_id.
    """