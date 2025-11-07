# 📋 REGRAS DE NEGÓCIO - SOLMAIOR
## Especificação Técnica para Implementação

**Versão:** 2.0 | **Data:** Outubro 2025 | **Status:** Ativo

---

## 1. REGRAS DE AGENDA E DISPONIBILIDADE

### RN-001: Definição de Disponibilidade do Professor

**Descrição:** Professor define seus dias e horários disponíveis para lecionar.

**Atores:** Professor, Admin

**Pré-condições:**
- Professor deve estar autenticado
- Deve ter perfil de professor criado

**Fluxo Principal:**
1. Professor acessa "Disponibilidade"
2. Seleciona dia da semana
3. Define horário de início e fim
4. Clica "Adicionar"
5. Sistema valida e salva
6. Exibe confirmação

**Validações:**
- Horário início < horário fim
- Não permitir sobreposição de horários no mesmo dia
- Horários devem estar em intervalos de 30 minutos
- Máximo 8 horas por dia

**Exceções:**
- E001: Horário inválido → Mensagem de erro
- E002: Sobreposição detectada → Alerta visual
- E003: Limite de horas excedido → Bloqueio

**Pós-condições:**
- Disponibilidade salva no banco
- Histórico de alteração registrado
- Agenda global atualizada

---

### RN-002: Agendamento de Aula

**Descrição:** Secretaria agenda aula vinculando aluno, professor, sala e horário.

**Atores:** Secretaria, Admin

**Pré-condições:**
- Aluno deve estar matriculado
- Professor deve ter disponibilidade
- Sala deve estar disponível
- Aluno não pode ter 1h de aulas na semana

**Fluxo Principal:**
1. Secretaria acessa "Agenda Global"
2. Clica em horário vazio
3. Preenche: Aluno, Professor, Sala, Duração
4. Sistema valida todas as regras
5. Se OK: Cria agendamento
6. Se Erro: Mostra mensagem

**Validações Obrigatórias:**
```
✓ Professor disponível no horário?
✓ Sala disponível no horário?
✓ Aluno sem conflito no horário?
✓ Aluno não excede 1h/semana?
✓ Duração é 30 ou 60 minutos?
✓ Horário está em intervalo de 30min?
```

**Matriz de Validação:**
| Validação | Condição | Ação |
|-----------|----------|------|
| Disponibilidade Professor | professor.availability.contains(horário) | ✅ Permite |
| Conflito Professor | LessonSchedule.where(professor_id, horário) | ❌ Bloqueia |
| Conflito Aluno | LessonSchedule.where(student_id, horário) | ❌ Bloqueia |
| Conflito Sala | LessonSchedule.where(room_id, horário) | ❌ Bloqueia |
| Limite Semanal | SUM(aulas_aluno_semana) + duração ≤ 60min | ✅ Permite |
| Duração | duração IN (30, 60) | ✅ Permite |

**Pós-condições:**
- LessonSchedule criado com status `confirmada`
- Room.status atualizado para `ocupada`
- Email de confirmação enviado
- Histórico de operação registrado

---

### RN-003: Validação de Conflitos

**Descrição:** Sistema detecta e impede conflitos automáticamente.

**Tipos de Conflito:**

#### Conflito de Professor
```
Condição: Professor tem 2 aulas no mesmo horário
Ação: ❌ Bloqueia agendamento
Mensagem: "Professor [nome] já tem aula de [hora] a [hora]"
```

#### Conflito de Aluno
```
Condição: Aluno tem 2 aulas no mesmo horário
Ação: ❌ Bloqueia agendamento
Mensagem: "Aluno [nome] já tem aula de [hora] a [hora]"
```

#### Conflito de Sala
```
Condição: Sala tem 2 aulas no mesmo horário
Ação: ❌ Bloqueia agendamento
Mensagem: "Sala [nome] já está ocupada de [hora] a [hora]"
```

#### Limite Semanal do Aluno
```
Condição: Aluno já tem 60 minutos de aulas na semana
Ação: ❌ Bloqueia agendamento
Mensagem: "Aluno já tem [X] minutos de aulas esta semana. Limite: 60 minutos"
```

#### Professor Indisponível
```
Condição: Horário está fora da disponibilidade do professor
Ação: ❌ Bloqueia agendamento
Mensagem: "Professor não está disponível neste horário"
```

---

### RN-004: Duração de Aulas

**Descrição:** Aulas podem ter 30 ou 60 minutos, máximo 60 minutos por semana por aluno.

**Opções de Duração:**
- 30 minutos (meia aula)
- 60 minutos (aula completa)

**Cálculo de Limite Semanal:**
```python
aulas_semana = LessonSchedule.filter(
    student_id=aluno_id,
    week=semana_atual,
    status!='cancelada'
).sum(duration)

if aulas_semana + nova_duracao > 60:
    BLOQUEIA("Limite de 60 minutos por semana excedido")
```

**Exemplos:**
- Aluno com 30min seg + 30min qua = ✅ OK (60min total)
- Aluno com 30min seg + 30min qua + 30min sex = ❌ BLOQUEADO (90min)
- Aluno com 60min seg = ✅ OK (60min total)
- Aluno com 60min seg + 30min qua = ❌ BLOQUEADO (90min)

---

### RN-005: Reserva de Salas

**Descrição:** Sistema reserva automaticamente a sala durante o horário da aula.

**Fluxo:**
1. Agendamento criado com sala_id
2. Room.status = `ocupada` para o horário
3. Fim da aula: Room.status = `disponível`
4. Histórico de ocupação mantido

**Validações:**
- Sala deve estar ativa (não desativada)
- Sala deve ter capacidade ≥ 1
- Sala não pode estar em manutenção

---

### RN-006: Atualização de Status

**Descrição:** Status da aula e sala são atualizados automaticamente.

**Estados de LessonSchedule:**
```
confirmada  → Aula agendada e confirmada
pendente    → Aguardando confirmação
cancelada   → Cancelada
reposição   → Aula de reposição
realizada   → Aula ocorreu
falta       → Aluno faltou
```

**Transições de Estado:**
```
confirmada  → realizada (fim do dia)
confirmada  → falta (fim do dia + ausência)
confirmada  → cancelada (cancelamento)
confirmada  → reposição (solicitação de reposição)
```

**Eventos que Disparam Atualização:**
- ✅ Novo agendamento → `confirmada`
- ✅ Cancelamento → `cancelada`
- ✅ Solicitação de reposição → `reposição`
- ✅ Fim do dia → `realizada` ou `falta`
- ✅ Pagamento recebido → Atualiza histórico financeiro

---

### RN-007: Fila de Espera para Aulas

**Descrição:** Sistema de fila de espera para capturar demanda não atendida.

**Entidade:** `LessonWaitlist`

**Fluxo:**
1. Aluno tenta agendar → sem disponibilidade
2. Sistema oferece: "Adicionar à fila de espera"
3. Aluno entra com preferências (dia/hora preferido)
4. Sistema monitora automaticamente
5. Quando horário fica livre:
   - Notifica aluno por email
   - Cria proposta de agendamento
   - Aluno confirma em 24h
   - Se não confirmar, passa para próximo

**Validações:**
- Máximo 30 dias na fila
- Prioridade por ordem de chegada
- Cancelamento automático se não confirmar em 24h
- Notificação automática quando disponível

**Benefícios:**
- Recupera 15-20% de alunos que não encontram horário
- Visibilidade de demanda não atendida
- Aumento de ocupação e receita

---

### RN-008: Reposição Inteligente com Sugestões Automáticas

**Descrição:** Sistema automático de sugestões de reposição.

**Entidade:** `MakeupLessonSuggestion`

**Fluxo:**
1. Aula cancelada ou falta detectada
2. Sistema cria solicitação de reposição
3. Busca 3 melhores horários:
   - Mesmo professor, mesma sala
   - Próximos 30 dias
   - Sem conflitos
4. Envia sugestões para aluno
5. Aluno escolhe uma opção
6. Se não responder em 7 dias:
   - Envia lembrete
   - Se ainda não responder: marca como "não compareceu"

**Validações:**
- Máximo 30 dias para reagendar
- 3 opções de horário sugeridas
- Notificação por email + SMS (futuro)
- Cancelamento automático se não responder em 7 dias

**Benefícios:**
- Reduz reposições não realizadas em 40%
- Automatiza sugestões
- Melhora experiência do aluno

---

### RN-009: Limite Semanal Dinâmico por Instrumento

**Descrição:** Limite de aulas varia conforme instrumento.

**Entidade:** `InstrumentLessonPolicy`

**Configuração Padrão:**

| Instrumento | Min | Max | Recomendado | Min Aulas | Max Aulas |
|-------------|-----|-----|-------------|-----------|-----------|
| Piano | 30 | 120 | 60 | 1 | 2 |
| Violão | 30 | 90 | 60 | 1 | 2 |
| Flauta | 20 | 60 | 30 | 1 | 1 |
| Canto | 30 | 60 | 60 | 1 | 1 |
| Bateria | 30 | 120 | 60 | 1 | 2 |

**Validações:**
- Cada instrumento tem política própria
- Validação usa limite do instrumento
- Admin pode customizar por escola
- Padrão: 30-60 minutos

**Benefícios:**
- Flexibilidade pedagógica
- Melhor adequação por instrumento
- Reduz conflitos de agenda

---

### RN-010: Sistema de Créditos de Aula

**Descrição:** Controle de aulas por créditos.

**Entidade:** `StudentLessonCredit`

**Fluxo:**
1. Matrícula define: "4 aulas por mês"
2. Sistema cria 4 créditos
3. Cada aula agendada: -1 crédito
4. Fim do mês:
   - Se sobrou: Oferece transferência para próximo mês
   - Se faltou: Oferece reposição
5. Relatório visual de uso

**Validações:**
- Créditos definidos na matrícula
- Válidos por período (mensal/trimestral)
- Transferência de créditos não usados
- Relatório de uso por aluno

**Benefícios:**
- Controle de uso de aulas
- Reduz desperdício
- Incentiva frequência

---

### RN-011: Desconto Progressivo por Frequência

**Descrição:** Desconto automático baseado em frequência.

**Tabela de Descontos:**

| Frequência | Desconto | Motivo |
|-----------|----------|--------|
| 100% | 10% | Frequência perfeita |
| 90-99% | 5% | Ótima frequência |
| 80-89% | 2% | Boa frequência |
| < 80% | 0% | Frequência baixa |

**Fluxo:**
1. Fim do mês: calcula frequência
2. Aplica desconto automático
3. Registra motivo: "Frequência 95%"
4. Notifica aluno: "Desconto de 5% por boa frequência!"
5. Desconto aparece na cobrança

**Validações:**
- Calculado automaticamente
- Aplicado na cobrança do mês
- Visível no recibo
- Histórico mantido

**Benefícios:**
- Reduz evasão em 20%
- Incentiva frequência
- Automático e transparente

---

## 2. REGRAS FINANCEIRAS

### RN-201: Mensalidade na Matrícula

**Descrição:** Cada aluno tem mensalidade definida no ato da matrícula.

**Campo:** `Student.monthly_fee` (Decimal)

**Fluxo de Matrícula:**
1. Secretaria cria novo aluno
2. Define mensalidade base (ex: R$ 200,00)
3. Sistema usa este valor para cobranças
4. Pode ser alterado no perfil do aluno

**Validações:**
- Mensalidade deve ser > 0
- Mensalidade deve ser numérica
- Máximo 2 casas decimais

---

### RN-202: Tipos de Pagamento

**Descrição:** Pagamento pode ser integral ou parcelado.

**Opções:**
1. **Integral** - Valor total à vista
2. **Parcelado** - 2 a 12 parcelas mensais

**Métodos de Pagamento:**
- 💳 PIX
- 💳 Cartão (Débito/Crédito)
- 💳 Boleto
- 💳 Transferência (TED/DOC)
- 💳 Dinheiro

**Fluxo de Pagamento Integral:**
```
1. Secretaria cria cobrança
2. Define tipo: "Integral"
3. Valor = monthly_fee - descontos
4. Aluno paga
5. Status = "pago"
```

**Fluxo de Pagamento Parcelado:**
```
1. Secretaria cria cobrança
2. Define tipo: "Parcelado"
3. Define número de parcelas (2-12)
4. Define data de vencimento da 1ª parcela
5. Sistema cria parcelas automaticamente
6. Cada parcela: valor_total / num_parcelas
7. Vencimentos: mensais a partir da 1ª data
```

**Exemplo de Parcelamento:**
```
Mensalidade: R$ 200,00
Parcelas: 4x
Valor por parcela: R$ 50,00

Parcela 1: R$ 50,00 - Vencimento: 01/11/2025
Parcela 2: R$ 50,00 - Vencimento: 01/12/2025
Parcela 3: R$ 50,00 - Vencimento: 01/01/2026
Parcela 4: R$ 50,00 - Vencimento: 01/02/2026
```

---

### RN-203: Sistema de Descontos

**Descrição:** Descontos percentuais ou fixos com registro de histórico.

**Tipos de Desconto:**
1. **Percentual** - Ex: 10%, 20%
2. **Fixo** - Ex: R$ 50,00

**Motivos de Desconto:**
- Bolsa de estudos
- Desconto por referência
- Promoção sazonal
- Dificuldade financeira
- Outro (campo livre)

**Fluxo de Desconto:**
```
1. Secretaria seleciona aluno
2. Clica "Aplicar Desconto"
3. Escolhe tipo: Percentual ou Fixo
4. Informa valor e motivo
5. Sistema calcula automaticamente
6. Exibe preview (valor original vs final)
7. Confirma aplicação
8. Registra no histórico
```

**Cálculo de Desconto:**
```
Desconto Percentual:
valor_desconto = monthly_fee * (percentual / 100)
valor_final = monthly_fee - valor_desconto

Desconto Fixo:
valor_final = monthly_fee - valor_fixo
```

**Validações:**
- Desconto não pode ser > 100% (percentual)
- Desconto não pode ser > monthly_fee (fixo)
- Motivo deve ser preenchido
- Histórico deve ser mantido

**Exemplo:**
```
Mensalidade: R$ 200,00
Desconto: 15% (Bolsa de estudos)
Valor desconto: R$ 30,00
Valor final: R$ 170,00
```

---

### RN-204: Materiais Didáticos

**Descrição:** Materiais obrigatórios ou opcionais associados ao aluno.

**Tipos de Material:**
- 📚 Apostilas
- 📚 Livros
- 🎵 Partituras
- 📰 Jornais
- 🎧 Áudios/Vídeos
- 📝 Outros

**Campos de MaterialDidatico:**
- `name` - Nome do material
- `description` - Descrição
- `price` - Preço unitário
- `type` - Tipo de material
- `instrument` - Instrumento associado
- `level` - Nível (iniciante, intermediário, avançado)
- `is_mandatory` - Obrigatório ou opcional
- `stock` - Quantidade em estoque

**Fluxo de Associação:**
```
1. Admin cadastra material
2. Define tipo, preço, instrumento, nível
3. Define se é obrigatório ou opcional
4. Secretaria associa ao aluno
5. Sistema adiciona ao valor da mensalidade
6. Aluno recebe material
7. Registra no histórico financeiro
```

**Validações:**
- Material deve ter preço > 0
- Material deve estar em estoque
- Aluno não pode ter material duplicado

---

### RN-205: Hora-Aula do Professor

**Descrição:** Valor da hora-aula para cálculo automático de pagamento.

**Campo:** `Teacher.hourly_rate` (Decimal)

**Fluxo:**
1. Admin define hora-aula do professor
2. Sistema calcula automaticamente
3. Relatório mensal: horas × valor

**Cálculo de Pagamento:**
```
horas_lecionadas = SUM(LessonSchedule.duration / 60)
    WHERE teacher_id = professor_id
    AND status IN ('realizada', 'falta')
    AND month = mes_atual

valor_a_receber = horas_lecionadas * hourly_rate
```

**Exemplo:**
```
Professor: João Silva
Hora-aula: R$ 50,00
Aulas ministradas: 20 horas
Valor a receber: R$ 1.000,00
```

---

### RN-206: Relatórios Financeiros

**Descrição:** Geração automática de relatórios mensais.

**Relatório 1: Pagamento de Professores**
```
Professor: [Nome]
Período: [Mês/Ano]
Total de aulas: [X]
Total de horas: [X]h
Hora-aula: R$ [X]
Valor a receber: R$ [X]
Status: [Pago/Pendente]
```

**Relatório 2: Alunos**
```
Aluno: [Nome]
Período: [Mês/Ano]
Mensalidade: R$ [X]
Descontos: R$ [X]
Valor final: R$ [X]
Status: [Pago/Pendente/Atrasado]
Aulas: [X]
```

**Relatório 3: Financeiro Geral**
```
Receita Total: R$ [X]
Receita Recebida: R$ [X]
Receita Pendente: R$ [X]
Receita em Atraso: R$ [X]
Despesas (Professores): R$ [X]
Lucro Líquido: R$ [X]
Margem: [X]%
```

**Relatório 4: Histórico de Transações**
```
Data: [Data/Hora]
Tipo: [Cobrança/Pagamento/Desconto]
Aluno: [Nome]
Valor: R$ [X]
Método: [PIX/Cartão/Boleto/etc]
Realizado por: [Usuário]
Motivo: [Motivo]
```

---

### RN-207: Histórico Financeiro

**Descrição:** Registro completo de todas as transações.

**Campos Registrados:**
- Data e hora da transação
- Tipo de transação (cobrança, pagamento, desconto)
- Aluno envolvido
- Valor
- Método de pagamento
- Quem realizou a ação
- Motivo (se aplicável)
- Status

**Auditoria:**
- Todas as transações são imutáveis
- Histórico não pode ser deletado
- Rastreabilidade completa

---

## 3. REGRAS DE RECITAIS

### RN-301: Criação de Evento

**Descrição:** Criação de recitais, audições e eventos artísticos.

**Campos Obrigatórios:**
- `title` - Título do evento
- `description` - Descrição
- `date` - Data
- `time` - Horário
- `location` - Local
- `capacity` - Capacidade
- `ticket_price` - Preço do ingresso
- `status` - Status do evento
- `is_public` - Público ou privado

**Campos Opcionais:**
- `dress_code` - Código de vestimenta
- `poster` - Cartaz do evento

**Status do Evento:**
- `planejado` - Em planejamento
- `confirmado` - Confirmado
- `realizado` - Evento ocorreu
- `cancelado` - Cancelado

**Validações:**
- Data deve ser futura
- Capacidade > 0
- Preço ≥ 0
- Descrição não vazia

---

### RN-302: Registro de Apresentações

**Descrição:** Registro de apresentações (solo, duplas, grupos, etc).

**Tipos de Apresentação:**
- Solo (1 aluno)
- Dupla (2 alunos)
- Trio (3 alunos)
- Grupo (4+ alunos)
- Coral (múltiplos alunos)
- Banda (múltiplos alunos)

**Campos:**
- `recital_id` - Evento
- `type` - Tipo de apresentação
- `order` - Ordem no programa
- `duration` - Duração estimada
- `composer` - Compositor
- `instrument` - Instrumento
- `teacher_id` - Professor orientador
- `description` - Descrição

**Fluxo:**
1. Admin cria evento
2. Adiciona apresentações
3. Define alunos participantes
4. Define ordem no programa
5. Define duração e compositor

---

### RN-303: Geração de Programa em PDF

**Descrição:** Programa automático em PDF com todas as apresentações.

**Conteúdo do Programa:**
- Cabeçalho com dados do evento
- Ordem das apresentações
- Informações de cada performance
- Compositor e instrumento
- Alunos participantes
- Professor orientador
- Rodapé com dados da escola

**Formato:**
- PDF profissional
- Fonte legível
- Cores da marca
- Logotipo da escola

---

### RN-304: Envio de Convites

**Descrição:** Envio automático de convites via email.

**Destinatários:**
- Alunos participantes
- Professores orientadores

**Conteúdo do Email:**
```
Olá [Nome]!

Você está convidado(a) para participar do evento:

📅 [Título do Recital]
📍 [Local]
🕐 [Data] às [Hora]

[Descrição]

👔 Traje: [Código de Vestimenta]

Por favor, confirme sua presença através do sistema.

[Link de confirmação]
```

**Validações:**
- Não enviar duplicado
- Registrar data/hora de envio
- Controle de entrega

---

### RN-305: Confirmação de Presença

**Descrição:** Alunos confirmam presença no evento.

**Status de Confirmação:**
- ⏳ Aguardando confirmação
- ✅ Confirmado
- ❌ Não comparecerá

**Fluxo:**
1. Aluno recebe convite
2. Acessa link de confirmação
3. Clica "Confirmar Presença" ou "Não Poderei Comparecer"
4. Sistema registra data/hora da confirmação
5. Admin vê contador de confirmados

---

### RN-306: Controle de Participantes

**Descrição:** Controle completo de presença e participação.

**Pós-Evento:**
- Admin marca presença/ausência
- Sistema registra data/hora
- Contador de presentes
- Identificação visual de cada tipo

---

### RN-307: Certificados de Participação

**Descrição:** Geração automática de certificados.

**Conteúdo:**
- Nome do aluno
- Evento
- Data
- Tipo de apresentação
- Compositor/Instrumento
- Assinatura digital
- Logotipo da escola

**Formato:**
- PDF profissional
- Certificado padrão
- Dados personalizados

---

## 4. REGRAS DE PAINEL ADMINISTRATIVO

### RN-401: Visão Centralizada

**Descrição:** Painel com visão completa da operação semanal.

**Informações Exibidas:**
- Professores e suas aulas
- Salas e ocupação
- Cursos e instrumentos
- Status das aulas
- Conflitos detectados
- Estatísticas

---

### RN-402: Filtros Avançados

**Filtros Disponíveis:**
- Por Professor
- Por Sala
- Por Status
- Por Instrumento/Curso
- Por Disponibilidade

**Combinações:**
- Filtros podem ser combinados
- Resultado em tempo real
- Atualização automática

---

### RN-403: Detecção de Conflitos

**Descrição:** Detecção automática de conflitos de horário.

**Tipos de Conflito:**
- Conflito de professor
- Conflito de aluno
- Conflito de sala

**Visualização:**
- Modo "Conflitos" no painel
- Comparação lado a lado
- Contador de conflitos
- Sugestões de resolução

---

### RN-404: Análises e Gráficos

**Análises Disponíveis:**
1. Taxa de Ocupação por Sala
2. Horas Lecionadas por Professor
3. Receita por Forma de Pagamento
4. Performance por Professor
5. Inadimplência

**Gráficos:**
- Barras
- Pizza
- Linha
- Gauge (semáforo)

---

## 5. REGRAS DE VALIDAÇÃO GERAL

### RN-501: Validação de Email

**Regra:** Email deve ser único e válido.

```
✓ Formato válido (RFC 5322)
✓ Não duplicado no banco
✓ Confirmação de email (futuro)
```

---

### RN-502: Validação de Senha

**Regra:** Senha deve ter segurança mínima.

```
✓ Mínimo 8 caracteres
✓ Pelo menos 1 letra maiúscula
✓ Pelo menos 1 número
✓ Pelo menos 1 caractere especial
✓ Hash com Werkzeug
```

---

### RN-503: Validação de Horário

**Regra:** Horários devem estar em intervalos válidos.

```
✓ Formato HH:MM
✓ Intervalo de 30 minutos
✓ Horário início < horário fim
✓ Dentro do horário comercial (06:00 - 22:00)
```

---

### RN-504: Validação de Data

**Regra:** Datas devem ser válidas e futuras.

```
✓ Formato YYYY-MM-DD
✓ Data válida
✓ Data ≥ hoje (para agendamentos)
✓ Data ≤ 1 ano no futuro
```

---

## 6. REGRAS DE SEGURANÇA

### RN-601: Proteção CSRF

**Regra:** Todos os formulários devem ter token CSRF.

```
✓ Token gerado automaticamente
✓ Token validado em POST/PUT/DELETE
✓ Token renovado a cada sessão
```

---

### RN-602: Controle de Acesso

**Regra:** Acesso baseado em papel (RBAC).

```
Admin:      Acesso total
Professor:  Apenas seus dados
Aluno:      Apenas seus dados
Secretaria: Dados operacionais
```

---

### RN-603: Auditoria Completa Financeira

**Regra:** Todas as operações financeiras são registradas de forma imutável.

**Entidade:** `FinancialAuditLog`

**Dados Registrados:**
```
✓ Quem fez (user_id)
✓ O que fez (action: create, update, delete, approve)
✓ Quando fez (timestamp)
✓ De onde fez (IP address)
✓ Valores antes/depois (old_value, new_value)
✓ Motivo da ação (reason)
✓ Status (success, failed)
```

**Eventos Auditados:**
- ✅ Criação de cobrança
- ✅ Aplicação de desconto
- ✅ Marcação de pagamento
- ✅ Alteração de mensalidade
- ✅ Cancelamento de parcela
- ✅ Reemissão de boleto
- ✅ Transferência de créditos

**Validações:**
- Todas operações registradas
- Imutável (append-only)
- Retenção: 7 anos
- Relatório de auditoria disponível

**Benefícios:**
- ✅ Conformidade LGPD
- ✅ Investigação de problemas
- ✅ Segurança aumentada
- ✅ Rastreabilidade 100%

---

## 7. REGRAS DE NOTIFICAÇÕES INTELIGENTES

### RN-801: Notificações com Priorização

**Regra:** Notificações são prorizadas e respeitam preferências do usuário.

**Entidade:** `NotificationPreference`

**Tipos de Notificação com Prioridade:**

| Tipo | Prioridade | Padrão | Canal |
|------|-----------|--------|-------|
| Aula em 24h | 🔴 Alta | Imediato | Email + SMS |
| Pagamento vencido | 🔴 Alta | Imediato | Email + SMS |
| Aula cancelada | 🟡 Média | Imediato | Email |
| Recital confirmado | 🟡 Média | Diário | Email |
| Notícia | 🟢 Baixa | Semanal | Email |

**Fluxo:**
1. Evento ocorre (aula agendada, pagamento vencido, etc)
2. Sistema verifica prioridade
3. Consulta preferências do usuário
4. Respeita horários silenciosos
5. Envia notificação no canal preferido

**Validações:**
- Priorização por tipo
- Respeita preferências do usuário
- Horários silenciosos (ex: 22h-08h)
- Histórico de notificações mantido
- Limite de frequência (máx 5 por dia)

**Benefícios:**
- ✅ Reduz spam
- ✅ Melhora engajamento
- ✅ Aumenta satisfação
- ✅ Respeita preferências

---

### RN-802: Dashboard Preditivo para Admin

**Regra:** Indicadores preditivos para decisões proativas.

**Indicadores Implementados:**

1. **Risco de Evasão**
   - Aluno com 2+ faltas consecutivas
   - Aluno com atraso em pagamento
   - Aluno sem aula há 30 dias
   - Ação: Notificar secretaria para contato

2. **Previsão de Receita**
   - Receita esperada próximos 30 dias
   - Receita em risco (inadimplência)
   - Receita confirmada
   - Gráfico de tendência

3. **Ocupação Prevista**
   - Taxa de ocupação próximas 4 semanas
   - Salas subutilizadas
   - Professores sobrecarregados
   - Sugestões de rebalanceamento

4. **Demanda Não Atendida**
   - Horários mais solicitados
   - Instrumentos com fila de espera
   - Professores com maior demanda
   - Sugestões de contratação

**Validações:**
- Atualização diária
- Alertas automáticos
- Histórico de previsões
- Acurácia monitorada

**Benefícios:**
- ✅ Decisões proativas
- ✅ Reduz evasão
- ✅ Otimiza recursos
- ✅ Aumenta receita

---

## 8. REGRAS DE PERFORMANCE

### RN-701: Cache

**Regra:** Dados frequentes são cacheados.

```
✓ Disponibilidade de professores (1 hora)
✓ Lista de salas (1 hora)
✓ Agenda semanal (30 minutos)
✓ Relatórios (1 dia)
```

---

### RN-702: Paginação

**Regra:** Listas grandes são paginadas.

```
✓ 20 itens por página (padrão)
✓ Navegação por página
✓ Busca rápida
✓ Ordenação
```

---

## 8. REGRAS DE NOTIFICAÇÃO

### RN-801: Email de Confirmação

**Regra:** Email enviado após agendamento.

```
✓ Para aluno
✓ Para professor
✓ Para secretaria
✓ Contém detalhes da aula
```

---

### RN-802: Lembrete de Aula

**Regra:** Lembrete enviado 24h antes da aula.

```
✓ Para aluno
✓ Para professor
✓ Contém horário e local
✓ Link para cancelamento
```

---

### RN-803: Notificação de Pagamento

**Regra:** Notificação de vencimento de parcela.

```
✓ 7 dias antes do vencimento
✓ No dia do vencimento
✓ 7 dias após atraso
✓ Contém valor e forma de pagamento
```

---

**Fim das Regras de Negócio**

Versão: 2.0 | Última atualização: Outubro 2025
