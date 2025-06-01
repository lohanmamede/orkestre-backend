from fastapi import APIRouter
from app.api.v1.endpoints import auth_router # Importa nosso router de autenticação

api_router = APIRouter()
api_router.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
# Futuramente, adicionaremos outros routers aqui (ex: para estabelecimentos, serviços)