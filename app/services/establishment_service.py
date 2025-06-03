# Este arquivo contém a lógica de negócios relacionada aos estabelecimentos.
# Ele interage com o banco de dados e aplica regras de negócio específicas.
from sqlalchemy.orm import Session
from typing import Optional

from app.models.establishment_model import Establishment
from app.schemas.working_hours_schema import WorkingHoursConfig # Nosso schema para os horários
# Precisaremos do schema Establishment para o tipo de retorno, se necessário
# from app.schemas.establishment_schema import Establishment as EstablishmentSchema 

# Uma função auxiliar para buscar um estabelecimento. Ela será útil nos nossos endpoints.
def get_establishment_by_id(db: Session, *, establishment_id: int) -> Optional[Establishment]:
    """
    Busca um estabelecimento pelo seu ID.
    """
    return db.query(Establishment).filter(Establishment.id == establishment_id).first()

""" Recebe o objeto Establishment já carregado do banco (establishment_db_obj) e os novos dados de horários (working_hours_in no formato do nosso schema WorkingHoursConfig).
    Converte o schema WorkingHoursConfig em um dicionário (working_hours_in.dict()) e o atribui ao campo working_hours_config do objeto Establishment. O SQLAlchemy (com o tipo JSON no modelo) e o driver do PostgreSQL cuidarão de serializar isso corretamente para o banco.
    Salva as alterações no banco."""
def update_establishment_working_hours(
    db: Session, 
    *, 
    establishment_db_obj: Establishment, # O objeto Establishment já buscado do banco
    working_hours_in: WorkingHoursConfig # Os novos dados de horários
) -> Establishment:
    """
    Atualiza a configuração de horários de atendimento de um estabelecimento.
    """
    establishment_db_obj.working_hours_config = working_hours_in.dict() # Salva o JSON no campo

    db.add(establishment_db_obj)
    db.commit()
    db.refresh(establishment_db_obj)
    return establishment_db_obj