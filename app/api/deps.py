# app/api/deps.py
from typing import Generator, Optional # Adicione Optional
from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer # Para pegar o token do header Authorization
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session
# from jose import JWTError # Importe JWTError se for tratar aqui também, mas security.py já trata

from app.db.session import SessionLocal
from app.core import security # Nosso módulo de segurança
from app.core.config import settings
from app.models.user_model import User # Nosso modelo User
from app.services import user_service # Para buscar o usuário


# Estava apresentando problemas com OAuth2PasswordBearer, então vamos usar HTTPBearer
# Não estava conseguindo fazer teste de login no Swagger com OAuth2PasswordBearer

# Define o esquema de autenticação OAuth2 (pega o token de 'Authorization: Bearer TOKEN')
# O tokenUrl pode apontar para o seu endpoint de login, é usado pela documentação do Swagger/OpenAPI.
# ALTERE A LINHA ABAIXO:
# De: reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")
# Para:
reusable_oauth2 = HTTPBearer(description="Insira o token Bearer JWT aqui para autorização")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
async def get_current_user( # Adicionar async é uma boa prática
    db: Session = Depends(get_db), 
    # ALTERE A LINHA ABAIXO para receber HTTPAuthorizationCredentials:
    http_credentials: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2)
) -> User:
    """
    Dependência para obter o usuário atual a partir do token JWT.
    Levanta HTTPException 401 se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"}, # Importante para o esquema Bearer
    )
    
    if http_credentials is None or http_credentials.scheme.lower() != "bearer":
        # Se o esquema não for Bearer ou se as credenciais não foram passadas
        raise credentials_exception

    token = http_credentials.credentials # Extrai o token da parte "Bearer <token>"
    
    try:
        user_email = security.verify_token_and_get_subject(
            token=token, credentials_exception=credentials_exception
        )
    except Exception: # Captura qualquer exceção de verify_token_and_get_subject
         raise credentials_exception

    user = user_service.get_user_by_email(db, email=user_email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para obter o usuário atual que também está ativo.
    Levanta HTTPException 400 se o usuário estiver inativo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")
    return current_user

"""
O que este código faz:
- get_db(): Esta função cria uma dependência que fornece uma sessão do banco de dados. Ela é usada para garantir que a sessão seja fechada corretamente após o uso.     
- reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=...): Esta é uma classe de utilidade do FastAPI que sabe como extrair o token do cabeçalho Authorization: Bearer TOKEN da requisição. O tokenUrl é usado pela documentação interativa /docs para saber onde o usuário pode obter um token.
- get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)):
    - Esta função de dependência primeiro pega a sessão do banco (db) e o token (extraído pelo reusable_oauth2).
    - Ela define uma credentials_exception padrão (HTTP 401).
    - Chama security.verify_token_and_get_subject para validar o token e obter o email do usuário. Se o token for inválido, a exceção é levantada.
    - Usa user_service.get_user_by_email para buscar o usuário no banco com o email obtido do token.
    - Se o usuário não for encontrado, levanta a credentials_exception.
    - Se tudo der certo, retorna o objeto User.
- get_current_active_user(current_user: User = Depends(get_current_user)):
    - Esta é outra dependência que depende da get_current_user.
    - Ela simplesmente pega o usuário retornado por get_current_user e verifica se current_user.is_active é True.
    - Se o usuário estiver inativo, levanta um erro HTTP 400.
    - Usaremos esta get_current_active_user nos nossos endpoints para garantir que apenas usuários ativos e autenticados possam realizar certas ações.
"""

""" Mudança de OAuth2PasswordBearer para HTTPBearer
- A mudança de OAuth2PasswordBearer para HTTPBearer foi feita porque o OAuth2PasswordBearer estava apresentando problemas ao tentar autenticar no Swagger. O HTTPBearer é uma alternativa que funciona bem para extrair o token do cabeçalho Authorization: Bearer TOKEN.   
- O HTTPBearer é mais simples e direto, especialmente se você não estiver usando o fluxo completo de OAuth2 com refresh tokens e tudo mais. Ele simplesmente extrai o token do cabeçalho e permite que você o valide.
# Explicação do Código  
Principais Mudanças no deps.py:

Mudamos OAuth2PasswordBearer para HTTPBearer(). O HTTPBearer simplesmente espera um token no cabeçalho Authorization: Bearer <token>.
- A dependência reusable_oauth2 agora é uma instância de HTTPBearer.
- A função get_current_user agora recebe http_credentials: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2).
- Dentro de get_current_user, verificamos se http_credentials não é nulo e se o esquema é "bearer".
- Extraímos o token de http_credentials.credentials.
- O restante da lógica para verificar o token e buscar o usuário permanece.
- Adicionar async à get_current_user é bom porque a busca no banco pode ser I/O bound.

"""