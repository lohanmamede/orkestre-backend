# Especificação Backend - Módulo de Profissionais

## Visão Geral

Esta especificação define os requisitos mínimos para implementação do módulo de profissionais no backend, mantendo compatibilidade com o frontend já desenvolvido. O backend tem autonomia para implementar seguindo os padrões já estabelecidos no projeto.

## Estrutura de Dados Esperada pelo Frontend

### Objeto Professional (Response)
```json
{
  "id": "string|uuid",
  "establishment_id": "string|uuid",
  "name": "string",
  "email": "string",
  "phone": "string|null",
  "specialty": "string|null",
  "description": "string|null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "services": [
    {
      "id": "string|uuid",
      "name": "string",
      "price": "number",
      "duration": "number"
    }
  ],
  "working_hours": {
    "monday": {
      "is_active": "boolean",
      "start_time": "string (HH:MM)",
      "end_time": "string (HH:MM)",
      "lunch_break_start_time": "string (HH:MM)|null",
      "lunch_break_end_time": "string (HH:MM)|null"
    },
    "tuesday": { /* mesmo formato */ },
    "wednesday": { /* mesmo formato */ },
    "thursday": { /* mesmo formato */ },
    "friday": { /* mesmo formato */ },
    "saturday": { /* mesmo formato */ },
    "sunday": { /* mesmo formato */ }
  },
  "total_appointments": "number",
  "monthly_appointments": "number",
  "total_revenue": "number",
  "monthly_revenue": "number",
  "rating": "number|null"
}
```

## Endpoints Necessários

### 1. Gestão de Profissionais

**POST** `/api/professionals`
```json
{
  "name": "string (obrigatório)",
  "email": "string (obrigatório)",
  "phone": "string (opcional)",
  "specialty": "string (opcional)",
  "description": "string (opcional)",
  "service_ids": ["uuid", "uuid"],
  "working_hours": {
    "monday": {
      "is_active": true,
      "start_time": "09:00",
      "end_time": "18:00",
      "lunch_break_start_time": "12:00",
      "lunch_break_end_time": "13:00"
    }
    // ... outros dias (opcional, pode ter default)
  }
}
```

**GET** `/api/professionals/establishment/{establishment_id}`
- Query params: `page`, `limit`, `search`, `status` (active/inactive/all)
- Response: Lista paginada ou array simples (decisão do backend)

**GET** `/api/professionals/{id}`
- Response: Objeto professional completo

**PUT** `/api/professionals/{id}`
- Body: Mesmo formato do POST
- Response: Professional atualizado

**DELETE** `/api/professionals/{id}`
- Response: Status de sucesso

**PATCH** `/api/professionals/{id}/status`
```json
{
  "is_active": "boolean"
}
```

### 2. Serviços do Profissional

**GET** `/api/professionals/{id}/services`
- Response: Array de serviços

**PUT** `/api/professionals/{id}/services`
```json
{
  "service_ids": ["uuid", "uuid"]
}
```

### 3. Horários de Trabalho

**GET** `/api/professionals/{id}/working-hours`
- Response: Objeto working_hours

**PUT** `/api/professionals/{id}/working-hours`
```json
{
  "working_hours": {
    "monday": { "is_active": true, "start_time": "09:00", "end_time": "18:00" },
    "tuesday": { "is_active": false }
    // ... outros dias
  }
}
```

### 4. Agendamentos e Estatísticas

**GET** `/api/professionals/{id}/appointments`
- Query params: `page`, `limit`, `date_from`, `date_to`, `status`
- Response: Lista de agendamentos (formato existente do sistema)

**GET** `/api/professionals/{id}/stats`
```json
{
  "total_appointments": "number",
  "monthly_appointments": "number", 
  "total_revenue": "number",
  "monthly_revenue": "number",
  "rating": "number|null",
  "recent_appointments": [
    {
      "id": "uuid",
      "client_name": "string",
      "service_name": "string", 
      "date": "datetime",
      "status": "string"
    }
  ]
}
```

## Regras de Negócio Mínimas

### Validações Obrigatórias
1. **Email único** - Profissional não pode ter email duplicado
2. **Establishment ownership** - Profissional deve pertencer ao estabelecimento do usuário autenticado
3. **Horários consistentes** - Se um dia está ativo, deve ter start_time e end_time válidos

### Validações Condicionais
4. **Serviços** - Profissional deve ter pelo menos um serviço atribuído **EXCETO** no primeiro cadastro (quando establishment não tem serviços ainda)
   - Permitir criação sem serviços se `services` do establishment estiver vazio
   - Após primeiro serviço ser criado no establishment, validação se torna obrigatória

### Validações Opcionais (autonomia do backend)
- Validação de formato de telefone
- Validação de horário de almoço
- Pelo menos um dia de trabalho ativo
- Outras validações que julgar necessárias

## Flexibilidades para o Backend

### Estrutura de Banco
- **Autonomia total** para decidir estrutura de tabelas
- Pode usar relacionamentos, JSON fields, ou outras abordagens
- Pode implementar soft delete ou hard delete
- Pode adicionar campos extras que julgar necessários

### Autenticação e Autorização
- Usar sistema de auth já implementado
- Seguir padrões de permissão já estabelecidos
- Filtrar por establishment conforme padrão atual

### Performance e Otimização
- Implementar paginação conforme padrão atual
- Usar cache se necessário
- Otimizar queries conforme experiência da equipe

### Logs e Auditoria
- Implementar conforme padrões já estabelecidos
- Logs de criação, edição, exclusão se necessário

## Pontos de Integração

### Com Serviços Existentes
- Usar tabela/modelo de Services já existente
- Relacionamento many-to-many entre Professional e Service

### Com Agendamentos (Futuro)
- Preparar campo `professional_id` na tabela de appointments
- Considerar relacionamento para futuras funcionalidades

### Com Estabelecimentos
- Usar relacionamento com tabela de establishments existente
- Filtrar sempre por establishment do usuário logado

## Considerações de Implementação

### Prioridade de Desenvolvimento
1. **CRUD básico** - Criar, listar, editar, excluir profissionais
2. **Relacionamento com serviços** - Atribuir/remover serviços
3. **Horários de trabalho** - Configuração de horários
4. **Estatísticas** - Cálculos de agendamentos e receita
5. **Integração com agendamentos** - Para quando módulo de agendamentos estiver pronto

### Sugestões (Não Obrigatórias)
- Considerar índices em campos de busca (name, email)
- Considerar cache para estatísticas se houver performance issues
- Implementar soft delete para manter histórico
- Considerar field `avatar_url` para foto do profissional (futuro)

## Testes Sugeridos

### Essenciais
- CRUD básico funcionando
- Validações de email único
- Filtro por establishment
- Relacionamento com serviços

### Opcionais
- Testes de performance com muitos profissionais
- Validações de horários
- Cálculo de estatísticas

---

**Nota:** Esta especificação foca apenas no que é necessário para o frontend funcionar. O backend tem total liberdade para implementar detalhes internos, estrutura de código, padrões de erro, logs, e outras funcionalidades seguindo os padrões já estabelecidos no projeto.