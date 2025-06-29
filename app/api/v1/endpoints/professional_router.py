from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.user_model import User
from app.schemas.professional_schema import Professional, ProfessionalCreate, ProfessionalUpdate
from app.services import establishment_service, professional_service

router = APIRouter()

@router.post("/establishments/{establishment_id}/professionals", response_model=Professional, status_code=status.HTTP_201_CREATED)
def create_new_professional(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int,
    professional_in: ProfessionalCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cria um novo profissional para um estabelecimento."""
    establishment = establishment_service.get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment or current_user not in establishment.users:
        raise HTTPException(status_code=403, detail="Não tem permissão para adicionar profissionais a este estabelecimento.")

    return professional_service.create_professional(db=db, professional_in=professional_in, establishment_id=establishment_id)

@router.get("/establishments/{establishment_id}/professionals", response_model=List[Professional])
def list_professionals_for_establishment(
    *,
    db: Session = Depends(deps.get_db),
    establishment_id: int
):
    """Lista os profissionais de um estabelecimento (endpoint público)."""
    return professional_service.get_professionals_by_establishment(db=db, establishment_id=establishment_id)

# Adicione aqui os endpoints para PUT e DELETE de um profissional se desejar, seguindo o mesmo padrão de segurança do POST.