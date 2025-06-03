# main.py
# Este arquivo é o ponto de entrada da aplicação FastAPI.
# Ele configura a aplicação, inicializa o banco de dados e inclui os routers da API.
from fastapi import FastAPI
from app.db.session import init_db # Importe a função
from app.api.v1.api import api_router as api_v1_router
from fastapi.middleware.cors import CORSMiddleware


# Chame init_db() aqui para criar as tabelas ao iniciar a aplicação
# Em um ambiente de produção, você usaria migrações (Alembic)
# Mas para o MVP e desenvolvimento local, isso é suficiente.
init_db() 

app = FastAPI(title="Orkestre Agenda API")

# Lista de origens permitidas (seu frontend em desenvolvimento)
origins = [
    "http://localhost:3000", # Endereço do seu frontend React
    # Você pode adicionar outras origens aqui se necessário, como o endereço de deploy do seu frontend no futuro
]

# Configuração do CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste conforme necessário para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chame init_db() aqui se não chamou antes, ou mantenha onde estava
# A ordem entre init_db() e app.add_middleware não deve ser crítica,
# mas geralmente middlewares vêm logo após a instância do app.
# Se init_db() faz chamadas ao banco na inicialização, certifique-se que o DB está pronto.
# Por segurança, vamos manter init_db() ANTES de adicionar o router, se ele já estava lá.
if not hasattr(app, 'db_initialized'): # Para garantir que init_db() seja chamado apenas uma vez
    init_db()
    app.db_initialized = True

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API Orkestre Agenda!"}

# Aqui adicionaremos os routers da API v1
app.include_router(api_v1_router, prefix="/api/v1")