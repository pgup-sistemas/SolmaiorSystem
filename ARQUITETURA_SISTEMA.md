# 🎼 SOLMAIOR - Arquitetura e Regras de Negócio
## Sistema de Gestão Integrado para Escola de Música

**Versão:** 2.0 | **Status:** Produção | **Cor Primária:** #008bcd (Azul Ciano)

---

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Regras de Negócio](#regras-de-negócio)
4. [Módulos Implementados](#módulos-implementados)
5. [Stack Tecnológica](#stack-tecnológica)
6. [Segurança e Conformidade](#segurança-e-conformidade)

---

## 🎯 Visão Geral

O **Sol Maior** é um sistema web integrado de gestão para escolas de música que centraliza:
- ✅ Controle de agenda de aulas
- ✅ Gestão de professores e alunos
- ✅ Administração financeira (mensalidades, descontos, parcelamentos)
- ✅ Gestão de recitais e eventos artísticos
- ✅ Painel macro administrativo com análises
- ✅ Portal público institucional

**Objetivo Principal:** Organizar e controlar todas as aulas da escola, disponíveis ou reservadas, respeitando a disponibilidade dos professores e a ocupação das salas.

---

## 🏗️ Arquitetura do Sistema

### Camadas da Aplicação

```
┌─────────────────────────────────────────────────────┐
│           Frontend (Tailwind CSS + Alpine.js)       │
├─────────────────────────────────────────────────────┤
│     API REST (Flask) - Rotas por Perfil             │
├─────────────────────────────────────────────────────┤
│  Lógica de Negócio (Services + Validações)          │
├─────────────────────────────────────────────────────┤
│     ORM SQLAlchemy (Models + Queries)               │
├─────────────────────────────────────────────────────┤
│        PostgreSQL (Banco de Dados)                  │
└─────────────────────────────────────────────────────┘
```

### Modelos de Dados Principais

```
User (Base)
├── Admin/Diretor
├── Teacher (Professores)
│   ├── TeacherAvailability (Disponibilidades)
│   └── hourly_rate (Valor hora-aula)
├── Student (Alunos)
│   ├── monthly_fee (Mensalidade)
│   ├── StudentMaterial (Materiais didáticos)
│   └── Installment (Parcelas)
└── Secretary (Secretaria)

LessonSchedule (Aulas)
├── teacher_id
├── student_id
├── room_id
├── status (confirmada, pendente, cancelada, reposição)
└── duration (30 ou 60 minutos)

Room (Salas)
├── capacity
└── equipment

Recital (Eventos)
├── RecitalPerformance (Apresentações)
└── RecitalParticipant (Participantes)

Financial (Financeiro)
├── Billing (Cobranças)
├── Discount (Descontos)
├── Installment (Parcelas)
└── MaterialDidatico (Materiais)
```

---

## 📋 Regras de Negócio

### 1️⃣ MÓDULO DE AGENDA E DISPONIBILIDADE

#### 1.1 Disponibilidade de Professores

**Regra:** O professor define previamente seus dias e horários disponíveis para lecionar.

- ✅ Professor acessa "Disponibilidade" no painel
- ✅ Define horários fixos (ex: Segunda 14h-18h, Quarta 10h-12h)
- ✅ Sistema valida se professor está disponível antes de agendar
- ✅ Interface visual mostra total de horas/semana
- ✅ Histórico de alterações mantido no banco de dados

**Validações:**
- Não permitir horários sobrepostos na mesma disponibilidade
- Validar se professor não está em aula em outro horário
- Impedir agendamento fora dos horários definidos

#### 1.2 Agendamento de Aulas

**Regra:** A secretaria ou admin cadastra os horários fixos na agenda global.

- ✅ Secretaria acessa "Agenda Global"
- ✅ Clica em horário vazio para agendar
- ✅ Sistema valida automaticamente todas as regras
- ✅ Só permite agendar se todos os critérios forem atendidos

**Fluxo de Agendamento:**
```
1. Secretaria seleciona horário vazio
2. Sistema valida:
   - Professor disponível?
   - Sala disponível?
   - Aluno sem conflito?
   - Aluno não excede 1h/semana?
3. Se OK: Cria agendamento
4. Se Erro: Mostra mensagem clara
```

#### 1.3 Validações Automáticas de Conflitos

**Regra:** O sistema impede conflitos de horário entre professores, salas e alunos.

- ✅ Verifica conflito de horário do professor
- ✅ Verifica conflito de horário do aluno
- ✅ Verifica conflito de sala
- ✅ Valida disponibilidade do professor
- ✅ Mostra apenas salas disponíveis no horário

**Matriz de Validação:**
| Validação | Descrição | Ação |
|-----------|-----------|------|
| Professor Ocupado | Professor já tem aula neste horário | ❌ Bloqueia |
| Aluno Ocupado | Aluno já tem aula neste horário | ❌ Bloqueia |
| Sala Ocupada | Sala já está reservada | ❌ Bloqueia |
| Professor Indisponível | Fora do horário definido | ❌ Bloqueia |
| Limite Semanal | Aluno já tem 1h de aulas | ❌ Bloqueia |
| Duração Inválida | Não é 30 ou 60 minutos | ❌ Bloqueia |

#### 1.4 Duração das Aulas

**Regra:** Alunos podem ter aulas de 30 minutos ou 1 hora, limitadas a 1 hora de aula por semana.

- ✅ Duração: 30 minutos ou 60 minutos
- ✅ Cálculo automático de horário de término
- ✅ Validação de conflitos considerando duração
- ✅ Limite máximo: 60 minutos por semana

**Exemplos:**
- Aula de 30min: 14:00-14:30 ✅
- Aula de 60min: 14:00-15:00 ✅
- Aula de 45min: ❌ Inválido
- Aluno com 30min + 30min na semana: ❌ Excede limite

#### 1.5 Reserva Automática de Salas

**Regra:** Cada professor ocupa uma sala específica durante os horários definidos, e o sistema reserva automaticamente a sala na agenda.

- ✅ Sistema mostra apenas salas disponíveis
- ✅ Impede agendamento em sala ocupada
- ✅ Atualização em tempo real
- ✅ Histórico de ocupação por sala

#### 1.6 Atualização de Status

**Regra:** O sistema atualiza automaticamente o status da sala e da agenda global após cada agendamento ou cancelamento.

**Status de Aula:**
- `confirmada` - Aula agendada e confirmada
- `pendente` - Aguardando confirmação
- `cancelada` - Cancelada pelo admin/professor
- `reposição` - Aula de reposição
- `realizada` - Aula ocorreu
- `falta` - Aluno faltou

**Eventos que Atualizam Status:**
- ✅ Novo agendamento → `confirmada`
- ✅ Cancelamento → `cancelada`
- ✅ Solicitação de reposição → `reposição`
- ✅ Fim do dia → `realizada` ou `falta`

---

### 2️⃣ MÓDULO FINANCEIRO E MENSALIDADES

#### 2.1 Mensalidade na Matrícula

**Regra:** Cada aluno tem sua mensalidade declarada no ato da matrícula.

- ✅ Campo `monthly_fee` na entidade Student
- ✅ Valor da mensalidade definido no cadastro
- ✅ Auto-preenchimento ao criar cobrança
- ✅ Pode ser alterado conforme necessidade

**Fluxo:**
```
1. Secretaria cria novo aluno
2. Define mensalidade base (ex: R$ 200,00)
3. Sistema usa este valor para cobranças
4. Pode ser alterado no perfil do aluno
```

#### 2.2 Tipos de Pagamento

**Regra:** O pagamento pode ser integral (valor total à vista) ou parcelado (em múltiplas parcelas mensais configuráveis).

**Opções de Pagamento:**
- 💳 **Integral** - Valor total à vista
- 💳 **Parcelado** - 2 a 12 parcelas mensais
- 💳 **PIX** - Transferência instantânea
- 💳 **Cartão** - Débito/Crédito
- 💳 **Boleto** - Cobrança bancária
- 💳 **Transferência** - TED/DOC
- 💳 **Dinheiro** - Pagamento em espécie

**Parcelamento:**
- Mínimo: 2 parcelas
- Máximo: 12 parcelas
- Vencimentos: Mensais automáticos
- Status por parcela: pendente, pago, atrasado

#### 2.3 Sistema de Descontos

**Regra:** O sistema permite aplicar descontos percentuais ou fixos, com registro no histórico financeiro.

- ✅ Desconto percentual (ex: 10%, 20%)
- ✅ Desconto fixo (ex: R$ 50,00)
- ✅ Registro do motivo do desconto
- ✅ Preview em tempo real do desconto
- ✅ Histórico completo de descontos aplicados
- ✅ Exibição visual do valor original vs valor com desconto

**Motivos de Desconto:**
- Bolsa de estudos
- Desconto por referência
- Promoção sazonal
- Dificuldade financeira
- Outro (campo livre)

**Exemplo:**
```
Mensalidade: R$ 200,00
Desconto: 15% (R$ 30,00)
Valor Final: R$ 170,00
```

#### 2.4 Materiais Didáticos

**Regra:** A mensalidade pode incluir materiais didáticos obrigatórios ou opcionais, como apostilas, livros, jornais e outros recursos utilizados nas aulas.

- ✅ Cadastro de materiais (apostilas, livros, partituras, jornais)
- ✅ Materiais Obrigatórios e Opcionais
- ✅ Preço individual por material
- ✅ Associação por instrumento e nível
- ✅ Controle de estoque
- ✅ Integração com financeiro do aluno

**Tipos de Materiais:**
- 📚 Apostilas
- 📚 Livros
- 🎵 Partituras
- 📰 Jornais
- 🎧 Áudios/Vídeos
- 📝 Outros

#### 2.5 Hora-Aula do Professor

**Regra:** Cada professor tem sua hora-aula declarada, usada para cálculo automático de relatórios de pagamento.

- ✅ Campo `hourly_rate` na entidade Teacher
- ✅ Cálculo automático de pagamento por horas lecionadas
- ✅ Relatório mensal de horas × valor

**Exemplo:**
```
Professor: João Silva
Hora-aula: R$ 50,00
Aulas ministradas: 20 horas
Valor a receber: R$ 1.000,00
```

#### 2.6 Relatórios Financeiros Automáticos

**Regra:** Geração automática de relatórios mensais com total de aulas ministradas, valores recebidos e pendências financeiras.

**Relatórios Disponíveis:**

1. **Relatório de Pagamento de Professores**
   - Total de horas por professor
   - Aulas ministradas
   - Cálculo: horas × valor hora-aula
   - Status de pagamento

2. **Relatório de Alunos**
   - Status de pagamentos por aluno
   - Mensalidades recebidas
   - Pendências
   - Descontos aplicados

3. **Relatório Financeiro Geral**
   - Receita total
   - Receita pendente
   - Receita em atraso
   - Despesas com professores
   - Lucro líquido
   - Margem de lucro

4. **Histórico de Transações**
   - Todas as transações registradas
   - Data, hora, valor, método
   - Quem fez cada ação
   - Motivos de descontos

#### 2.7 Histórico Financeiro

**Regra:** Registro de todas as transações no histórico financeiro.

- ✅ Registro de todas transações
- ✅ Descontos aplicados
- ✅ Pagamentos recebidos
- ✅ Quem fez cada ação
- ✅ Data e hora de cada transação
- ✅ Rastreabilidade completa

---

### 3️⃣ MÓDULO DE RECITAIS E PROGRAMAS ARTÍSTICOS

#### 3.1 Criação de Eventos

**Regra:** Criação de eventos (recitais, audições, semanas da música).

- ✅ Título, descrição, data, horário, local
- ✅ Capacidade de público
- ✅ Preço de ingresso (gratuito ou pago)
- ✅ Código de vestimenta
- ✅ Upload de cartaz do evento
- ✅ Status (planejado, confirmado, realizado, cancelado)
- ✅ Evento público ou privado

**Campos do Evento:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| title | String | ✅ | Nome do evento |
| description | Text | ✅ | Descrição detalhada |
| date | Date | ✅ | Data do evento |
| time | Time | ✅ | Horário de início |
| location | String | ✅ | Local do evento |
| capacity | Integer | ✅ | Capacidade de público |
| ticket_price | Decimal | ✅ | Preço do ingresso |
| dress_code | String | ❌ | Código de vestimenta |
| poster | File | ❌ | Cartaz do evento |
| status | Enum | ✅ | Status do evento |
| is_public | Boolean | ✅ | Público ou privado |

#### 3.2 Registro de Apresentações

**Regra:** Registro de apresentações (solo, duplas, bandas, corais).

- ✅ Solo/Individual
- ✅ Duplas
- ✅ Grupos
- ✅ Coral
- ✅ Banda
- ✅ Múltiplos alunos por apresentação
- ✅ Professor orientador
- ✅ Ordem no programa
- ✅ Duração estimada
- ✅ Compositor e instrumento

**Tipos de Apresentação:**
```
Solo (1 aluno)
Dupla (2 alunos)
Trio (3 alunos)
Grupo (4+ alunos)
Coral (múltiplos alunos)
Banda (múltiplos alunos com instrumentos variados)
```

#### 3.3 Programa em PDF

**Regra:** Geração automática de programa em PDF e certificados de participação.

- ✅ Download do programa completo
- ✅ Formatação profissional
- ✅ Ordem das apresentações
- ✅ Informações de cada performance
- ✅ Dados do evento
- ✅ Certificados individuais para cada aluno

#### 3.4 Envio de Convites e Lembretes

**Regra:** Envio automático de convites e lembretes via e-mail.

- ✅ Email para todos os alunos participantes
- ✅ Email para professores orientadores
- ✅ Informações completas do evento
- ✅ Controle de envio (não envia duplicado)
- ✅ Data e hora do envio registrada
- ✅ Badge visual indicando "Convites enviados"

**Email de Convite:**
```
Olá [Nome]!

Você está convidado(a) para participar do evento:

📅 [Título do Recital]
📍 [Local]
🕐 [Data] às [Hora]

[Descrição]

👔 Traje: [Código de Vestimenta]

Por favor, confirme sua presença através do sistema.
```

#### 3.5 Painel de Confirmação de Presença

**Regra:** Painel para confirmação de presença e controle de participantes.

- ✅ Botão "Confirmar Presença" para alunos
- ✅ Botão "Não Poderei Comparecer"
- ✅ Status visual de confirmação
- ✅ Data da confirmação registrada
- ✅ Contador de confirmados
- ✅ Destaque visual para suas apresentações

**Status de Confirmação:**
- ⏳ Aguardando confirmação
- ✅ Confirmado
- ❌ Não comparecerá
- ✓ Presente (pós-evento)
- ✗ Ausente (pós-evento)

#### 3.6 Controle de Participantes

**Regra:** Controle completo de participantes e presença.

- ✅ Lista completa de apresentações
- ✅ Status de cada participante
- ✅ Marcação de presença/ausência (pós-evento)
- ✅ Contador de presentes
- ✅ Identificação visual de cada tipo de apresentação

---

### 4️⃣ PAINEL MACRO ADMINISTRATIVO

#### 4.1 Visão Centralizada

**Regra:** Visão centralizada de toda a operação semanal.

- ✅ Exibição de professores, salas, cursos e status das aulas
- ✅ Filtros por professor, sala, curso e disponibilidade
- ✅ Detecção automática de conflitos de horários
- ✅ Gráficos analíticos de ocupação e horas lecionadas
- ✅ Relatórios de desempenho, ociosidade e reposições

#### 4.2 Três Modos de Visualização

**Modo Grade (Grid):**
- Visualização semanal tradicional com todos os horários
- Cores por status de aula
- Clique em horário vazio para agendar

**Modo Análises (Analytics):**
- Gráficos e estatísticas de ocupação
- Taxa de ocupação por sala
- Horas lecionadas por professor
- Receita por forma de pagamento
- Performance por professor

**Modo Conflitos:**
- Detecção automática de sobreposições
- Visualização detalhada de cada conflito
- Comparação lado a lado das aulas conflitantes
- Contador de conflitos em tempo real

#### 4.3 Filtros Avançados

- ✅ Por Professor
- ✅ Por Sala
- ✅ Por Status
- ✅ Por Instrumento/Curso
- ✅ Por Disponibilidade (ocupados/livres)

#### 4.4 Indicadores Operacionais

**KPIs Monitorados:**
| Indicador | Descrição | Meta |
|-----------|-----------|------|
| Taxa de Ocupação | % de salas ocupadas | > 80% |
| Horas Lecionadas | Total de horas/semana | Crescente |
| Taxa de Conversão | Aulas confirmadas / agendadas | > 90% |
| Taxa de Inadimplência | Alunos com atraso / total | < 10% |
| Reposições Pendentes | Aulas a repor | Mínimo |

---

## 🎯 Módulos Implementados

### ✅ Módulo 1: Autenticação e Autorização
- Login/Logout com Flask-Login
- 4 níveis de acesso: Admin, Professor, Aluno, Secretaria
- Proteção de rotas por papel
- Controle de sessão

### ✅ Módulo 2: Gestão de Agenda
- Disponibilidade de professores
- Agendamento de aulas
- Validações automáticas
- Reserva de salas
- Histórico de alterações

### ✅ Módulo 3: Gestão Financeira
- Mensalidades
- Descontos (percentual e fixo)
- Parcelamentos (2-12x)
- Materiais didáticos
- Relatórios financeiros
- Histórico de transações

### ✅ Módulo 4: Recitais e Eventos
- Criação de eventos
- Registro de apresentações
- Geração de programa em PDF
- Envio de convites
- Confirmação de presença
- Certificados de participação

### ✅ Módulo 5: Painel Administrativo
- Visão centralizada
- Três modos de visualização
- Filtros avançados
- Detecção de conflitos
- Análises e gráficos
- Relatórios exportáveis

### ✅ Módulo 6: Portal Público
- Landing page institucional
- Formulário de aula experimental
- Seção de notícias e eventos
- Design responsivo

---

## 🛠️ Stack Tecnológica

### Backend
- **Flask 3.0.0** - Framework web Python
- **Flask-SQLAlchemy 3.1.1** - ORM para PostgreSQL
- **Flask-Login 0.6.3** - Sistema de autenticação
- **Flask-JWT-Extended 4.6.0** - Tokens JWT
- **Flask-Mail 0.9.1** - Envio de emails
- **PostgreSQL** - Banco de dados relacional
- **Psycopg2-binary 2.9.9** - Driver PostgreSQL

### Frontend
- **Tailwind CSS** - Framework CSS (via CDN)
- **Alpine.js** - Framework JavaScript leve
- **Font Awesome** - Ícones
- **Vanilla JavaScript** - Manipulação DOM

### Padrão de Cores
- **Cor Primária:** #008bcd (Azul Ciano)
- **Gradiente:** cyan-600 → blue-600
- **Semáforo:** Verde (OK), Amarelo (Atenção), Vermelho (Erro)

---

## 🔐 Segurança e Conformidade

### Proteção CSRF
- Flask-WTF configurado
- Tokens CSRF automáticos em todos os formulários

### Validação de Dados
- Validação de campos obrigatórios
- Verificação de duplicidade de emails
- Tratamento de erros com rollback de transações
- Mensagens de erro informativas

### Autenticação
- Senhas hashadas com Werkzeug
- Controle de sessão com Flask-Login
- Proteção de rotas por papel

### Auditoria
- Registro de todas as transações financeiras
- Rastreamento de quem fez cada ação
- Data e hora de cada operação
- Histórico de alterações de disponibilidade

---

## 📊 Estrutura de Diretórios

```
solmaior/
├── app/
│   ├── __init__.py
│   ├── models.py              # Modelos do banco
│   ├── routes/
│   │   ├── auth.py            # Autenticação
│   │   ├── admin.py           # Painel admin
│   │   ├── teacher.py         # Painel professor
│   │   ├── student.py         # Painel aluno
│   │   ├── secretary.py       # Painel secretaria
│   │   ├── public.py          # Portal público
│   │   ├── documents.py       # Documentos
│   │   ├── financial.py       # Financeiro
│   │   └── recitals.py        # Recitais
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── teacher/
│   │   ├── student/
│   │   ├── secretary/
│   │   ├── public/
│   │   ├── financial/
│   │   └── recitals/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
└── ARQUITETURA_SISTEMA.md
```

---

## 🚀 Próximas Fases

### Fase 3: Automações RPA
- Bot de lembrete diário de aulas
- Bot de detecção e marcação de faltas
- Bot de sugestão de reposições
- Bot de auditoria semanal
- Bot de otimização de agenda mensal

### Fase 4: Integrações
- Gateways de pagamento (PIX, Cartão, Boleto)
- Google Calendar
- WhatsApp Business API
- Integração com sistemas bancários

### Fase 5: Analytics Avançado
- Dashboards preditivos
- Machine Learning para otimização
- Análise de tendências
- Recomendações automáticas

---

## 📞 Suporte e Manutenção

**Responsáveis:**
- **Arquitetura:** Engenheiro Senior
- **Backend:** Desenvolvedor Python/Flask
- **Frontend:** Desenvolvedor Frontend
- **DevOps:** Engenheiro de Infraestrutura

**Contato:** [email de suporte]

---

**Última atualização:** Outubro 2025
**Versão:** 2.0 - Arquitetura Consolidada
