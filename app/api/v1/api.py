from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, service_router  # Importa nosso router de autenticação

api_router = APIRouter()
api_router.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
api_router.include_router(service_router.router, prefix="", tags=["Services"]) # Ajuste o prefixo se necessário
# Exemplo de prefixo para serviços: /services ou manter no raiz da v1 para /services/{service_id}
# Se o prefixo for "", as rotas serão /services/{service_id} e /establishments/{id}/services/
# Se o prefixo for "/services", as rotas seriam /services/services/{service_id} (ruim)
# Vamos manter prefix="" por enquanto para o router de serviço, ou podemos ser mais específicos nas rotas
# Ou podemos criar um router para /establishments e aninhar os serviços nele.
# Por simplicidade agora, vamos manter prefix="" e as rotas como definidas no service_router.