# app/services/professional_service.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.professional_model import Professional
from app.schemas.professional_schema import ProfessionalCreate, ProfessionalUpdate

def create_professional(db: Session, *, professional_in: ProfessionalCreate, establishment_id: int) -> Professional:
    """Cria um novo profissional para um estabelecimento."""
    db_professional = Professional(
        **professional_in.dict(),
        establishment_id=establishment_id
    )
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    return db_professional

def get_professionals_by_establishment(db: Session, *, establishment_id: int) -> List[Professional]:
    """Lista todos os profissionais de um estabelecimento."""
    return db.query(Professional).filter(Professional.establishment_id == establishment_id).all()

def update_professional(db: Session, *, professional_db_obj: Professional, professional_in: ProfessionalUpdate) -> Professional:
    """Atualiza um profissional."""
    update_data = professional_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(professional_db_obj, field, value)
    db.add(professional_db_obj)
    db.commit()
    db.refresh(professional_db_obj)
    return professional_db_obj

def delete_professional(db: Session, *, professional_id: int) -> Optional[Professional]:
    """Deleta um profissional."""
    db_professional = db.query(Professional).filter(Professional.id == professional_id).first()
    if db_professional:
        db.delete(db_professional)
        db.commit()
    return db_professional