# Orkestre Backend API

## 📋 Visão Geral

O **Orkestre Backend** é uma API REST robusta desenvolvida com FastAPI para gerenciar agendamentos de serviços para estabelecimentos como pet shops, clínicas veterinárias e salões de beleza. O sistema oferece funcionalidades completas de autenticação, gerenciamento de estabelecimentos, serviços e agendamentos.

### 🎯 Principais Funcionalidades

- **Autenticação JWT**: Sistema seguro de login e registro
- **Gerenciamento de Estabelecimentos**: Configuração de horários de funcionamento e informações
- **Gestão de Serviços**: CRUD completo para serviços oferecidos
- **Sistema de Agendamentos**: Agendamento inteligente com validações de horário
- **API RESTful**: Endpoints bem estruturados seguindo padrões REST
- **Documentação Interativa**: Swagger UI e ReDoc automáticos

## 🏗️ Arquitetura

### Estrutura do Projeto

```
orkestre-backend/
├── app/
│   ├── api/                    # Camada de API
│   │   ├── deps.py            # Dependências compartilhadas
│   │   └── v1/                # API versão 1
│   │       ├── api.py         # Router principal
│   │       └── endpoints/     # Endpoints específicos
│   │           ├── auth_router.py
│   │           ├── user_router.py
│   │           ├── establishment_router.py
│   │           ├── service_router.py
│   │           └── appointment_router.py
│   ├── core/                  # Configurações centrais
│   │   ├── config.py         # Configurações da aplicação
│   │   └── security.py       # Segurança e JWT
│   ├── db/                   # Camada de banco de dados
│   │   ├── base_class.py     # Classe base SQLAlchemy
│   │   └── session.py        # Configuração de sessão
│   ├── models/               # Modelos SQLAlchemy
│   │   ├── user_model.py
│   │   ├── establishment_model.py
│   │   ├── service_model.py
│   │   └── appointment_model.py
│   ├── schemas/              # Schemas Pydantic
│   │   ├── base_schema.py
│   │   ├── user_schema.py
│   │   ├── establishment_schema.py
│   │   ├── service_schema.py
│   │   ├── appointment_schema.py
│   │   └── working_hours_schema.py
│   ├── services/             # Lógica de negócio
│   │   ├── user_service.py
│   │   ├── establishment_service.py
│   │   ├── service_service.py
│   │   └── appointment_service.py
│   └── main.py              # Ponto de entrada da aplicação
├── docker-compose.yml        # Configuração Docker
├── requirements.txt          # Dependências Python
└── README.md                # Documentação
```

### Padrão Arquitetural

O projeto segue o padrão **Clean Architecture** com separação clara de responsabilidades:

- **API Layer**: Controllers e validação de entrada
- **Service Layer**: Lógica de negócio
- **Data Layer**: Modelos e acesso a dados
- **Core**: Configurações e utilitários compartilhados

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e performático
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e filas (configurado no Docker)
- **Pydantic**: Validação de dados e serialização
- **JWT**: Autenticação via tokens
- **Passlib**: Hash de senhas com bcrypt
- **Uvicorn**: Servidor ASGI

## 📦 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- PostgreSQL (ou use o Docker Compose fornecido)

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd orkestre-backend
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados
DATABASE_URL=postgresql://orkestre_user:32423r32d32ed32423423423@localhost:5432/orkestre_db

# Segurança JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Execute o Banco de Dados (Docker)

```bash
docker-compose up -d
```

Isso iniciará:
- PostgreSQL na porta `5432`
- Redis na porta `6379`

### 5. Execute a Aplicação

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

### Documentação Interativa

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Autenticação

Todos os endpoints protegidos requerem autenticação via Bearer Token:

```http
Authorization: Bearer <your-jwt-token>
```

## 🔗 Endpoints da API

### Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/register` | Registrar novo usuário | ❌ |
| POST | `/login` | Login do usuário | ❌ |

#### Exemplo de Registro

```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
  "establishment_name": "Pet Shop ABC"
}
```

#### Exemplo de Login

```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Usuários (`/api/v1/users`)

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/me` | Perfil do usuário logado | ✅ |

### Estabelecimentos (`/api/v1/establishments`)

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| PUT | `/{establishment_id}/working-hours` | Configurar horários de funcionamento | ✅ |

#### Exemplo de Configuração de Horários

```json
PUT /api/v1/establishments/1/working-hours
{
  "monday": {
    "is_active": true,
    "start_time": "08:00",
    "end_time": "18:00",
    "lunch_break_start_time": "12:00",
    "lunch_break_end_time": "13:00"
  },
  "tuesday": {
    "is_active": true,
    "start_time": "08:00",
    "end_time": "18:00"
  },
  "appointment_interval_minutes": 30
}
```

### Serviços (`/api/v1`)

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/establishments/{establishment_id}/services/` | Criar serviço | ✅ |
| GET | `/establishments/{establishment_id}/services/` | Listar serviços | ❌ |
| GET | `/services/{service_id}` | Obter serviço específico | ❌ |
| PUT | `/services/{service_id}` | Atualizar serviço | ✅ |
| DELETE | `/services/{service_id}` | Excluir serviço | ✅ |

#### Exemplo de Criação de Serviço

```json
POST /api/v1/establishments/1/services/
{
  "name": "Banho e Tosa Completo",
  "description": "Banho, escovação, corte de unhas e perfume",
  "price": 75.50,
  "duration_minutes": 90,
  "is_active": true
}
```

### Agendamentos (`/api/v1`)

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/establishments/{establishment_id}/appointments/` | Criar agendamento | ❌* |
| GET | `/establishments/{establishment_id}/appointments/` | Listar agendamentos | ✅ |
| GET | `/appointments/{appointment_id}` | Obter agendamento específico | ✅ |
| PATCH | `/appointments/{appointment_id}/status` | Atualizar status | ✅ |

*Cliente final pode agendar sem login

#### Exemplo de Criação de Agendamento

```json
POST /api/v1/establishments/1/appointments/
{
  "service_id": 1,
  "customer_name": "João Silva",
  "customer_phone": "(11) 99999-9999",
  "customer_email": "joao@email.com",
  "appointment_datetime": "2024-01-15T14:30:00",
  "notes": "Pet com medo de barulho"
}
```

## 🗄️ Modelo de Dados

### Relacionamentos

```
User (1) ──── (1) Establishment
Establishment (1) ──── (N) Service
Establishment (1) ──── (N) Appointment
Service (1) ──── (N) Appointment
```

### Principais Entidades

#### User
- `id`: ID único
- `email`: Email único
- `password_hash`: Senha criptografada
- `is_active`: Status ativo/inativo
- `created_at`: Data de criação

#### Establishment
- `id`: ID único
- `name`: Nome do estabelecimento
- `phone_number`: Telefone
- `working_hours_config`: Configuração de horários (JSON)
- `user_id`: Referência ao usuário proprietário

#### Service
- `id`: ID único
- `name`: Nome do serviço
- `description`: Descrição
- `price`: Preço
- `duration_minutes`: Duração em minutos
- `is_active`: Status ativo/inativo
- `establishment_id`: Referência ao estabelecimento

#### Appointment
- `id`: ID único
- `service_id`: Referência ao serviço
- `establishment_id`: Referência ao estabelecimento
- `customer_name`: Nome do cliente
- `customer_phone`: Telefone do cliente
- `customer_email`: Email do cliente
- `appointment_datetime`: Data e hora do agendamento
- `status`: Status do agendamento
- `notes`: Observações

### Status de Agendamento

```python
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"      # Agendado
    CONFIRMED = "confirmed"      # Confirmado
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"      # Concluído
    CANCELLED = "cancelled"      # Cancelado
    NO_SHOW = "no_show"         # Não compareceu
```

## 🔒 Segurança

### Autenticação JWT

- Tokens com expiração configurável
- Hash de senhas com bcrypt
- Validação automática de tokens

### Autorização

- Verificação de propriedade de recursos
- Endpoints protegidos por usuário
- Separação entre operações públicas e privadas

### CORS

Configurado para aceitar requisições do frontend (desenvolvimento):
- `http://localhost:3000`

## 🚀 Deploy

### Produção

Para deploy em produção, considere:

1. **Variáveis de Ambiente**: Configure adequadamente
2. **CORS**: Ajuste as origens permitidas
3. **HTTPS**: Use certificados SSL/TLS
4. **Banco de Dados**: Configure conexão segura
5. **Logs**: Implemente logging apropriado

### Docker

```bash
# Build da imagem
docker build -t orkestre-backend .

# Executar container
docker run -p 8000:8000 orkestre-backend
```

## 🧪 Testes

### Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest
```

### Testar APIs

Use a documentação interativa em `/docs` ou ferramentas como:
- Postman
- Insomnia
- curl

### Exemplos de Teste

```bash
# Registrar usuário
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "establishment_name": "Test Pet Shop"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## 📈 Monitoramento

### Logs

A aplicação registra automaticamente:
- Requisições HTTP
- Erros de autenticação
- Operações de banco de dados
- Validações de agendamento

### Health Check

```bash
curl http://localhost:8000/
```

## 🔧 Configurações Avançadas

### Banco de Dados

Configurações personalizadas em `app/core/config.py`:

```python
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

### Cache Redis

Configurado para uso futuro em filas e cache:

```python
REDIS_URL = "redis://localhost:6379"
```

## 🤝 Contribuição

### Padrões de Código

- Use Black para formatação
- Siga PEP 8
- Documente funções públicas
- Escreva testes para novas funcionalidades

### Estrutura de Commits

```
type(scope): description

feat(auth): add password reset functionality
fix(appointments): resolve timezone issue
docs(api): update endpoint documentation
```

## 📝 Changelog

### v1.0.0 (MVP)
- ✅ Sistema de autenticação JWT
- ✅ CRUD de usuários
- ✅ CRUD de estabelecimentos
- ✅ CRUD de serviços
- ✅ Sistema de agendamentos
- ✅ Configuração de horários de funcionamento
- ✅ Documentação API completa

### Próximas Versões
- 🔄 Sistema de notificações
- 🔄 Relatórios e analytics
- 🔄 Integração com pagamentos
- 🔄 App mobile
- 🔄 Multi-tenancy

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte a documentação interativa em `/docs`
2. Verifique os logs da aplicação
3. Abra uma issue no repositório
4. Entre em contato com a equipe de desenvolvimento

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Orkestre Backend** - Sistema de Agendamento Inteligente 🎼

Desenvolvido com ❤️ usando FastAPI e as melhores práticas de desenvolvimento Python.
