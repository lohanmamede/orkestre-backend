# Este arquivo contém a lógica de negócios relacionada aos estabelecimentos.
# Ele interage com o banco de dados e aplica regras de negócio específicas.
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.service_model import Service # Nosso modelo SQLAlchemy
from app.models.establishment_model import Establishment # Para verificar a qual estabelecimento o serviço pertence
from app.schemas.service_schema import ServiceCreate, ServiceUpdate # Nossos schemas Pydantic

# --- FUNÇÕES CRUD PARA SERVIÇOS ---

def create_establishment_service(db: Session, *, service_in: ServiceCreate, establishment_id: int) -> Service:
    """
    Cria um novo serviço para um estabelecimento específico.
    """
    db_service = Service(
        **service_in.dict(), # Pega todos os dados do schema ServiceCreate
        establishment_id=establishment_id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_service(db: Session, *, service_id: int) -> Optional[Service]:
    """
    Obtém um serviço pelo seu ID.
    """
    return db.query(Service).filter(Service.id == service_id).first()

def get_services_by_establishment(db: Session, *, establishment_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
    """
    Obtém uma lista de serviços pertencentes a um estabelecimento específico, com paginação.
    """
    return db.query(Service).filter(Service.establishment_id == establishment_id).offset(skip).limit(limit).all()

def update_service(db: Session, *, service_db_obj: Service, service_in: ServiceUpdate) -> Service:
    """
    Atualiza um serviço existente.
    service_db_obj: o objeto Service já recuperado do banco.
    service_in: um schema ServiceUpdate com os campos a serem atualizados.
    """
    update_data = service_in.dict(exclude_unset=True) # Pega só os campos que foram enviados para atualização
    for field, value in update_data.items():
        setattr(service_db_obj, field, value)

    db.add(service_db_obj) # Adiciona o objeto modificado à sessão
    db.commit()
    db.refresh(service_db_obj)
    return service_db_obj

def delete_service(db: Session, *, service_id: int) -> Service | None:
    """
    Deleta um serviço pelo seu ID.
    Retorna o objeto deletado ou None se não encontrado.
    """
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
    return db_service

# --- FUNÇÕES DE VERIFICAÇÃO (Podemos adicionar mais depois) ---

def check_establishment_exists(db: Session, *, establishment_id: int) -> Optional[Establishment]:
    """
    Verifica se um estabelecimento existe.
    """
    return db.query(Establishment).filter(Establishment.id == establishment_id).first()

    """
    Explicação das Funções no service_service.py:

    create_establishment_service(...):
        - Recebe a sessão do banco (db), os dados do novo serviço (service_in no formato ServiceCreate), e o establishment_id ao qual o serviço pertencerá.
        - service_in.dict(): Converte o schema Pydantic em um dicionário, que pode ser usado para preencher os campos do modelo SQLAlchemy Service usando ** (desempacotamento de dicionário).
        - Adiciona, comita e refresca o novo objeto Service no banco.
    get_service(...):
        - Busca um único serviço pelo seu service_id. Retorna o objeto Service ou None.
    get_services_by_establishment(...):
        - Busca todos os serviços que pertencem a um establishment_id específico.
        - Inclui parâmetros skip e limit para uma paginação simples (útil se um estabelecimento tiver muitos serviços).
    update_service(...):
        - Recebe o objeto Service que já foi buscado do banco (service_db_obj) e os dados para atualização (service_in no formato ServiceUpdate).
        - service_in.dict(exclude_unset=True): Pega apenas os campos que foram realmente enviados no corpo da requisição de atualização (se um campo não foi enviado, ele não será atualizado para None por engano).
        - Usa setattr para atualizar os campos do objeto service_db_obj com os novos valores.
        - Adiciona, comita e refresca.
    delete_service(...):
        - Busca o serviço pelo service_id.
        - Se encontrar, deleta do banco e comita.
        - Retorna o objeto deletado (ou None se não encontrou).
    check_establishment_exists(...):
        - Uma função auxiliar simples para verificar se um estabelecimento com o ID fornecido existe. Usaremos isso nos nossos endpoints para garantir que estamos tentando adicionar serviços a um estabelecimento válido.
    
    Considerações de Segurança/Permissão (Para o Futuro Próximo):
    
    Verificação de Proprietário: Nas funções create_establishment_service, update_service, e delete_service, e também nos endpoints que as chamarão, precisaremos adicionar uma lógica para garantir que o usuário autenticado é o proprietário do establishment_id em questão. Não queremos que um usuário adicione serviços ao estabelecimento de outro!
        - Isso geralmente envolve pegar o user_id do token JWT do usuário logado e verificar se esse user_id corresponde ao user_id associado ao establishment_id.
    Por enquanto, essas funções de serviço estão focadas no CRUD em si. A camada de endpoints da API (que faremos a seguir) será o local onde aplicaremos a lógica de autenticação e autorização.
    """