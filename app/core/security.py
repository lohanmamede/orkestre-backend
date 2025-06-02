from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import JWTError, jwt # Biblioteca para JWT
from passlib.context import CryptContext

from app.core.config import settings # Nossas configurações (SECRET_KEY, ALGORITHM, etc.)
from app.schemas.user_schema import TokenData # Precisaremos do schema TokenData.

# PWD_CONTEXT (se decidir movê-lo para cá do user_service.py, senão pode remover daqui)
# PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def get_password_hash(password: str) -> str:
#     return PWD_CONTEXT.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return PWD_CONTEXT.verify(plain_password, hashed_password)

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Cria um novo token de acesso JWT.
    :param subject: O "assunto" do token (geralmente o ID ou email do usuário).
    :param expires_delta: Tempo opcional para expiração do token. Se não fornecido, usa o padrão das configurações.
    :return: O token JWT codificado como string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- NOVA FUNÇÃO OU FINALIZAÇÃO DA ESBOÇADA ---
def verify_token_and_get_subject(token: str, credentials_exception: Exception) -> str:
    """
    Decodifica o token JWT. Se válido, retorna o 'subject' (email).
    Se inválido ou expirado, levanta a credentials_exception.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(email=email) # Poderíamos validar com TokenData se ele tivesse mais campos
        return email # Retorna diretamente o email (subject)
    except JWTError: # Se o token for inválido (expirado, assinatura errada, etc.)
        raise credentials_exception

"""
Mudanças/Adições:
- A função verify_token_and_get_subject (renomeei para ser mais clara que ela retorna o subject) agora está completa.
- Ela tenta decodificar o token usando jwt.decode.
- Pega o sub (que é o email do nosso usuário) do payload do token.
- Se o email não existir ou se houver qualquer JWTError (token expirado, assinatura inválida, etc.), ela levanta a credentials_exception que será passada como argumento (esta exceção virá do FastAPI, geralmente um HTTPException com status 401).
- Se tudo estiver ok, ela retorna o email do usuário.
Nota sobre PWD_CONTEXT: Eu comentei as funções de senha aqui. Se você as manteve no user_service.py, está perfeito. Se quiser centralizar toda a segurança (tokens e senhas) aqui, poderia movê-las para cá. Por agora, o importante é a verify_token_and_get_subject.
"""