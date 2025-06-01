from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt # Biblioteca para JWT
from passlib.context import CryptContext

from app.core.config import settings # Nossas configurações (SECRET_KEY, ALGORITHM, etc.)

# Já tínhamos isso no user_service.py, vamos centralizar aqui ou manter lá e importar?
# Por ora, para manter o foco no token, vou assumir que as funções de senha estão no user_service.
# Se quisermos centralizar tudo de segurança aqui, podemos mover PWD_CONTEXT, get_password_hash, verify_password para cá.
# Por agora, focaremos apenas no token.

# PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto") # Se fosse mover para cá

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

# Futuramente, podemos adicionar uma função para decodificar/validar tokens aqui também,
# para proteger endpoints.
# def verify_token(token: str, credentials_exception):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#         token_data = TokenData(email=email) # TokenData do user_schema.py
#     except JWTError:
#         raise credentials_exception
#     return token_data