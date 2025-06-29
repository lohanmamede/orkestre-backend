# Este arquivo contém a lógica de negócios relacionada aos estabelecimentos.
# Ele interage com o banco de dados e aplica regras de negócio específicas.
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.models.establishment_model import Establishment
from app.schemas.working_hours_schema import WorkingHoursConfig # Nosso schema para os horários

from app.models.user_model import User
from app.services import user_service
from app.models.role_enum import Role
from app.models.user_establishment_link import user_establishment_link # Importa a tabela de associação

from app.schemas.establishment_schema import Establishment as EstablishmentSchema, MemberSchema


def get_establishment_by_id(db: Session, *, establishment_id: int) -> Optional[Establishment]:
    """
    Busca um estabelecimento pelo seu ID.
    """
    return db.query(Establishment).filter(Establishment.id == establishment_id).first()

def add_collaborator(
    db: Session, *, establishment: Establishment, collaborator_email: str
) -> Establishment:
    """
    Adiciona um usuário existente como colaborador a um estabelecimento.
    """
    collaborator_user = user_service.get_user_by_email(db, email=collaborator_email)
    if not collaborator_user:
        raise ValueError(f"Nenhum usuário encontrado com o e-mail: {collaborator_email}")

    is_already_member = db.query(user_establishment_link).filter_by(
        user_id=collaborator_user.id,
        establishment_id=establishment.id
    ).first() is not None

    if is_already_member:
        raise ValueError("Este usuário já é um membro deste estabelecimento.")
    
    establishment.users.append(collaborator_user)
    
    db.add(establishment)
    db.commit()
    
    return establishment

def remove_collaborator(
    db: Session, *, establishment: Establishment, collaborator_to_remove: User
) -> Establishment:
    """
    Remove um usuário colaborador de um estabelecimento.
    """
    # Verifica se o usuário a ser removido é realmente um membro
    if collaborator_to_remove not in establishment.users:
        raise ValueError("Este usuário não é um membro deste estabelecimento.")

    # Verifica se não está tentando remover o único OWNER (regra de negócio importante)
    link = db.query(user_establishment_link).filter_by(user_id=collaborator_to_remove.id, establishment_id=establishment.id).first()
    if link and link.role == Role.OWNER:
        # Conta quantos owners existem para este estabelecimento
        owner_count = db.query(user_establishment_link).filter_by(establishment_id=establishment.id, role=Role.OWNER).count()
        if owner_count <= 1:
            raise ValueError("Não é possível remover o único proprietário do estabelecimento.")

    # Remove a associação
    establishment.users.remove(collaborator_to_remove)

    db.add(establishment)
    db.commit()

    return establishment

def get_establishment_for_api_response(db: Session, *, establishment_id: int) -> Optional[EstablishmentSchema]:
    """
    Busca um estabelecimento e monta o schema Pydantic de resposta,
    incluindo a lista de membros com seus papéis, de forma segura.
    """
    establishment = get_establishment_by_id(db, establishment_id=establishment_id)
    if not establishment:
        return None

    # Query que busca os usuários e seus papéis para este estabelecimento
    members_data = db.query(
        User,
        user_establishment_link.c.role
    ).join(
        user_establishment_link, user_establishment_link.c.user_id == User.id
    ).filter(
        user_establishment_link.c.establishment_id == establishment_id
    ).all()

    # Monta a lista de membros no formato do MemberSchema
    members_list = [
        MemberSchema(id=user.id, email=user.email, role=role)
        for user, role in members_data
    ]

    # Constrói o objeto Pydantic de resposta manualmente, campo por campo
    establishment_response = EstablishmentSchema(
        id=establishment.id,
        name=establishment.name,
        phone_number=establishment.phone_number,
        timezone=establishment.timezone,
        display_address=establishment.display_address,
        about_text=establishment.about_text,
        users=members_list
        # Adicione aqui quaisquer outros campos do schema Establishment
    )
    
    return establishment_response

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