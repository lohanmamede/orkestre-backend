# Este arquivo é o api.py que define o router principal da API v1, incluindo os outros routers específicos como autenticação e serviços.
from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, service_router, establishment_router, appointment_router

api_router = APIRouter()
api_router.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
api_router.include_router(service_router.router, prefix="", tags=["Services"])
api_router.include_router(establishment_router.router, prefix="/establishments", tags=["Establishments"]) # NOVO ROUTER
# Ajuste o prefixo se necessário
# Exemplo de prefixo para serviços: /services ou manter no raiz da v1 para /services/{service_id}
# Se o prefixo for "", as rotas serão /services/{service_id} e /establishments/{id}/services/
# Se o prefixo for "/services", as rotas seriam /services/services/{service_id} (ruim)
# Vamos manter prefix="" por enquanto para o router de serviço, ou podemos ser mais específicos nas rotas
# Ou podemos criar um router para /establishments e aninhar os serviços nele.
# Por simplicidade agora, vamos manter prefix="" e as rotas como definidas no service_router.

# O prefixo para appointments pode ser aninhado sob establishments ou ser próprio.
# Se for aninhado como no endpoint de criação, o router principal não precisa de prefixo para ele.
# Ou podemos ter um prefixo /appointments e as rotas serem /appointments/ e /appointments/{id}
# Para manter o POST /establishments/{id}/appointments/ e GET /establishments/{id}/appointments/,
# podemos incluir o router sem um prefixo global para ele aqui, ou com um prefixo que não conflite.
# Por agora, vamos manter as rotas como definidas no appointment_router.
# O FastAPI é inteligente para montar as rotas.
api_router.include_router(appointment_router.router, tags=["Appointments"]) # Adicionando tags para organização no /docs