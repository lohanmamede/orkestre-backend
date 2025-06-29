# Sistema de Usuários e Profissionais - Redesign

## Instruções para Implementação

### Mudanças Estruturais Importantes

**Situação Atual:**
- Relacionamento 1:1 entre usuário e estabelecimento
- Cada usuário pertence a apenas um estabelecimento
- Cada estabelecimento pertence a apenas um usuário

**Nova Arquitetura:**
- Relacionamento N:N entre usuários e estabelecimentos
- Um usuário pode ter acesso a múltiplos estabelecimentos
- Um estabelecimento pode ter múltiplos usuários
- Sistema de contexto ativo (qual estabelecimento está gerenciando)
- Roles e permissões específicas por estabelecimento
- Suporte a expansão de negócios e múltiplas unidades

### Tipos de Entidade Redefinidos

**Usuários do Sistema (com login):**
- OWNER - Proprietário do estabelecimento
- COLLABORATOR - Demais usuários com permissões customizáveis definidas pelo owner

**Profissionais (sem login):**
- PROFESSIONAL - Prestadores de serviço cadastrados pelo owner
- Apenas para identificação em agendamentos
- Sem acesso ao sistema

### Distinção Importante: Usuários vs Profissionais

**Usuários do Sistema (com login e acesso):**
- Fazem login no sistema
- Têm permissões e roles definidos
- Podem gerenciar estabelecimentos, agendamentos, etc.
- Geram cobrança no plano (usuários extras)

**Profissionais (sem login, apenas cadastro):**
- NÃO fazem login no sistema
- Apenas dados cadastrais para identificação
- Aparecem nos agendamentos como "quem vai atender"
- Cadastrados e gerenciados pelos usuários (OWNER/COLLABORATOR)
- NÃO geram cobrança adicional



### Sistema de Permissões

**Permissões Disponíveis:**
- Definir com base no que é oferecido no momento de funcionalidades.

**Lógica de Permissões:**
- OWNER tem todas as permissões automaticamente para seus estabelecimentos
- COLLABORATOR tem permissões definidas pelo owner do estabelecimento
- Permissões são específicas por estabelecimento (usuário pode ter roles diferentes em cada)
- Validação de permissões considera estabelecimento ativo na sessão
- Implementar decorator/middleware que verifica permissão + contexto do estabelecimento

### Fluxo de Onboarding Simplificado

**Primeira pergunta:**
"Você é:"
- Proprietário (criar estabelecimento)
- Colaborador (juntar-se a estabelecimento)

**Para Proprietários:**
- Cadastro pessoal → Dados do estabelecimento
- "Você atende sozinho ou tem equipe de profissionais?"
- Setup inicial de profissionais se aplicável
- Após primeiro estabelecimento, opção de criar novos estabelecimentos

**Para Colaboradores:**
- Dados pessoais → Código/email do estabelecimento
- Aguardar aprovação do owner com definição de permissões

### Gestão de Múltiplos Estabelecimentos

**Seletor de Contexto:**
- Após login, usuário vê lista de estabelecimentos com acesso
- Seleção define o estabelecimento ativo na sessão
- UI com switcher no header para alternar rapidamente
- Breadcrumb mostrando estabelecimento atual

**Criação de Novos Estabelecimentos:**
- Owner pode criar quantos estabelecimentos quiser (não a princípio)
- Fluxo simplificado: reutiliza dados pessoais, pede apenas dados do novo estabelecimento
- Cada estabelecimento é independente em termos de colaboradores e profissionais
- Cobrança por estabelecimento conforme plano escolhido

### Sistema de Convites Redesenhado

**Convite de Colaboradores:**
- Owner envia convite por email/código
- Define permissões específicas no momento do convite
- Colaborador aceita e recebe acesso conforme permissões
- Cobrança adicional por usuário extra no plano

**Gerenciamento de Profissionais:**
- Owner cadastra profissionais sem acesso ao sistema
- Profissionais aparecem apenas para seleção em agendamentos
- Não geram custo adicional (não são usuários do sistema)


### Validações e Regras de Negócio

**Estabelecimento:**
- Deve ter exatamente um OWNER
- Pode ter N colaboradores
- Pode ter N profissionais

**Usuário:**
- Pode ter acesso a múltiplos estabelecimentos com roles diferentes
- Colaborador só pode ter permissões definidas pelo owner
- Owner não pode se auto-remover se for o único
- Colaborador removido perde acesso imediatamente
- Contexto de estabelecimento ativo determina permissões aplicáveis

**Profissional:**
- Pode ser atribuído a múltiplos agendamentos
- Remoção só permitida se não tiver agendamentos futuros
- Desativação em vez de exclusão para manter histórico

### Benefícios da Nova Arquitetura

1. **Suporte a Múltiplos Estabelecimentos:** Permite que usuário tenha diferentes roles em estabelecimentos diferentes
2. **Expansão de Negócios:** Facilita crescimento de profissionais autônomos para múltiplas unidades
3. **Flexibilidade de Roles:** Owner define permissões específicas por colaborador e estabelecimento
4. **Escalabilidade:** Funciona desde profissional individual até redes de franquias
5. **Simplicidade de UX:** Apenas 2 tipos de usuário no onboarding, contexto claro por sessão
6. **Vantagem Competitiva:** Diferencial importante no mercado de gestão de estabelecimentos
7. **Controle de Custos:** Profissionais não geram cobrança adicional, apenas colaboradores
8. **Separação Clara:** Usuários do sistema vs prestadores de serviço

### Cenários de Uso Contemplados

**Profissional Individual:**
- Cabeleireira que trabalha em salão e quer abrir estúdio próprio
- Pode ser colaboradora no salão e owner do estúdio
- Um login, dois contextos diferentes

**Expansão de Negócios:**
- Dentista que tem consultório e quer abrir filial
- Owner de ambos os estabelecimentos
- Gerencia ambos com mesmo login

**Franquias e Redes:**
- Franqueado que expande para múltiplas unidades
- Owner de todos os estabelecimentos da rede
- Visão consolidada ou por unidade
