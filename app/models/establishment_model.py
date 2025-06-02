from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# No topo de app/models/establishment_model.py
# from .service_model import Service # Ou use a string "Service" no relationship
#Importe Service no topo (cuidado com importação circular - talvez seja melhor usar string): Porém, para relationship, é comum usar a string com o nome da classe se houver risco de importação circular ou se o modelo ainda não foi definido quando o Python lê o arquivo. Mas como Service estará em seu próprio arquivo, podemos tentar o import direto. Se der erro de importação circular, usaremos a string.



class Establishment(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    # working_hours_config = Column(JSON, nullable=True) # Para guardar config de horários

    user_id = Column(Integer, ForeignKey("users.id")) # Chave estrangeira para users.id
    user = relationship("User", back_populates="establishment") # Relacionamento de volta para User
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relacionamento com os serviços deste estabelecimento
    services = relationship(
        "Service", # Nome da Classe do modelo relacionado
        back_populates="establishment", # Nome do atributo no modelo Service que aponta de volta
        cascade="all, delete-orphan" # Se um estabelecimento for deletado, seus serviços também serão
    )