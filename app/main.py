from fastapi import FastAPI
from app.db.session import init_db # Importe a função
from app.api.v1.api import api_router as api_v1_router

# Chame init_db() aqui para criar as tabelas ao iniciar a aplicação
# Em um ambiente de produção, você usaria migrações (Alembic)
# Mas para o MVP e desenvolvimento local, isso é suficiente.
init_db() 

app = FastAPI(title="Orkestre Agenda API")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API Orkestre Agenda!"}

# Aqui adicionaremos os routers da API v1
app.include_router(api_v1_router, prefix="/api/v1")