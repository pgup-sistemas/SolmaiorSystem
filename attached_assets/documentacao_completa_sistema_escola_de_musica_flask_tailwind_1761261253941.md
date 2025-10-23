# 📘 Documentação Completa — Sistema de Escola de Música (Flask + Tailwind CSS)

---

## 🏫 Visão Geral do Sistema
Sistema web completo para gestão de uma **Escola de Música**, desenvolvido em **Python (Flask)** e **Tailwind CSS**, com funcionalidades voltadas para administração, professores, alunos e secretaria. Inclui módulos de **agenda, recitais, reposições, controle financeiro, documentos, e portal administrativo público**.

---

## 🧩 Módulos Principais

### 1️⃣ Gestão de Usuários e Perfis
- Cadastro e autenticação de **alunos, professores, secretaria e admin**.
- Perfis com níveis de acesso e permissões distintas.
- Integração com autenticação via e-mail/senha e token JWT.

**Papéis:**
| Papel | Acesso / Ações |
|--------|----------------|
| **Admin/Diretor** | Controle total, define políticas, cria usuários, aprova eventos, gerencia agenda global e recitais. |
| **Secretaria** | Responsável por matrículas, agendamentos, reposições e relatórios. |
| **Professor** | Define disponibilidade semanal, acessa materiais, confirma presença e acompanha aulas. |
| **Aluno** | Visualiza aulas, eventos, materiais e agenda pessoal. |

---

### 2️⃣ Portal Público e Administrativo (Landing Page)
- Página inicial com informações da escola e formulário de **agendamento de aula experimental**.
- Seção de **notícias e eventos**, atualizada pelo admin.
- Painel de login para acesso ao sistema (professores, alunos e secretaria).

**Funcionalidades:**
- Gerenciamento de postagens (notícias, eventos, recitais).
- Galeria de fotos e vídeos.
- Formulário integrado com notificações automáticas via e-mail (Flask-Mail).

---

### 3️⃣ Gestão Acadêmica (Agenda e Reposição de Aulas)

#### 🎯 Objetivo
Gerenciar horários de aulas, reposições e alocação de salas de forma organizada e automatizada, com controle de permissões e disponibilidade.

#### 👥 Papéis e Permissões
| Papel | Função |
|--------|---------|
| **Professor** | Define disponibilidade semanal (dias/horários). |
| **Secretaria** | Agenda alunos, gerencia reposições, controla salas. |
| **Admin/Diretor** | Supervisiona todas as agendas e define políticas. |
| **Aluno** | Visualiza horários e confirma presença. |

#### 🧭 Fluxo Operacional
1. **Professor define disponibilidade** → via grade semanal.
2. **Secretaria agenda alunos** conforme disponibilidade e matrícula.
3. **Reposições** são registradas apenas pela secretaria/admin, com regras automáticas.
4. Sistema valida conflitos de horário e ocupa salas automaticamente.

**Tabelas-chave:**
- `teacher_availability`
- `lesson_schedule`
- `makeup_lessons`

#### 🤖 RPA (Automação de Agenda e Reposição)
| Bot | Função | Frequência |
|------|---------|------------|
| **Bot de Lembrete de Aula** | Notifica alunos/professores sobre aulas do dia. | Diário |
| **Bot de Faltas** | Marca aulas não confirmadas como faltas. | Diário |
| **Bot de Reposição** | Sugere horários disponíveis para reposição. | 2x semana |
| **Bot de Auditoria** | Gera relatórios de reposições e faltas. | Semanal |
| **Bot de Otimização de Agenda** | Reorganiza horários livres. | Mensal |

---

### 4️⃣ Módulo de Recitais e Programação Artística
Gerencia eventos, apresentações e recitais da escola.

**Funcionalidades:**
- Criação de eventos (recitais, audições, semanas da música).
- Registro de apresentações (individual, dupla, grupo, coral, banda).
- Associação de alunos e professores a cada apresentação.
- Confirmação de participação e geração automática do programa do evento (PDF).

**Tabelas:**
- `recitals`
- `recital_performances`
- `recital_participants`

**Automação (RPA):**
- Geração automática de programas e certificados.
- Envio de convites e lembretes.
- Bot de atualização de status de confirmações.

---

### 5️⃣ Painel Macro Administrativo — Agenda Global

#### 🎯 Objetivo
Dar ao **Admin/Diretor** uma visão centralizada e interativa de toda a operação semanal: horários de professores, ocupação de salas, e status de aulas/reposições.

#### 🧩 Funcionalidades
- **Visão global por semana:** tabela interativa com status de aulas (livre, ocupado, reposição, conflito).
- **Filtros inteligentes:** busca por professor, instrumento, sala, turno ou status.
- **Mapa de ocupação de salas:** exibição gráfica tipo mapa de calor.
- **Detecção automática de conflitos:** bloqueio de sobreposições de professor/sala.
- **Relatórios analíticos:** taxa de ocupação, horas lecionadas, tempo ocioso, e reposições.

#### 🧮 Estrutura de Dados
- `admin_global_view` (visão agregada)
- `room_schedule` (join entre `lesson_schedule` e `rooms`)
- `schedule_conflicts` (controle de sobreposição)

#### 🤖 Automação (RPA)
| Bot | Função | Frequência |
|------|---------|------------|
| **Bot de Atualização da Visão Macro** | Atualiza painel global após agendamentos. | Em tempo real |
| **Bot de Conflitos** | Detecta sobreposições de horários. | Imediato |
| **Bot de Alertas de Ociosidade** | Relata horários vagos e sugestões. | Semanal |
| **Bot de Relatórios de Desempenho** | Gera KPIs mensais da operação. | Mensal |

#### 🖥️ Interface (UI/UX)
- Layout tipo **FullCalendar.js** + **Tailwind grid**.
- Tooltips e cores para status de horários.
- Modo leitura para professores e modo edição para secretaria/admin.

#### 🔐 Permissões
- **Admin/Secretaria:** acesso total.  
- **Professor:** somente sua própria agenda.  
- **Aluno:** apenas suas aulas confirmadas.

---

### 6️⃣ Módulo Financeiro e Documental
- Controle de mensalidades, pagamentos e inadimplência.
- Emissão automática de recibos e relatórios.
- Upload e armazenamento de documentos (contratos, partituras, PDFs, áudios, vídeos).

---

### 7️⃣ Estrutura Técnica (Stack)
- **Backend:** Flask + SQLAlchemy + Celery + Redis + PostgreSQL.
- **Frontend:** Tailwind CSS + Alpine.js + FullCalendar.js.
- **Storage:** AWS S3 ou Google Cloud Storage.
- **RPA:** Celery Tasks + Cron Scheduler.
- **Autenticação:** JWT / Flask-Login.

---

### 8️⃣ Benefícios Gerais
- Centralização completa da gestão pedagógica e administrativa.  
- Evita conflitos de horários e uso incorreto de salas.  
- Automatiza reposições, relatórios e comunicação.  
- Fornece visão global da operação para diretores e administradores.  
- Flexível, escalável e compatível com uso comercial real.

---

## ✅ Conclusão
Esta documentação define toda a arquitetura e automação (RPA) de um **sistema completo para escolas de música**, cobrindo desde a gestão de alunos e professores até o controle de agenda, recitais e financeiro — tudo integrado com automações, controle de permissões e visão macro administrativa pronta para implantação comercial.

