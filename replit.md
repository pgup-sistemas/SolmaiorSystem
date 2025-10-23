# Solmaior - Sistema de Gestão para Escola de Música

## 📋 Visão Geral
Sistema web completo para gestão de escola de música desenvolvido em **Python (Flask)** e **Tailwind CSS**, com funcionalidades voltadas para administração, professores, alunos e secretaria.

## 🎯 Objetivo
Gerenciar completamente uma escola de música, incluindo:
- Gestão de usuários e perfis
- Controle de agenda e horários
- Sistema de reposições de aulas
- Gestão de recitais e eventos
- Portal público institucional
- Painel macro administrativo

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

## 📁 Estrutura do Projeto

```
workspace/
├── app/
│   ├── __init__.py          # Inicialização do app Flask
│   ├── models.py            # Modelos do banco de dados
│   ├── routes/              # Rotas e controllers
│   │   ├── auth.py          # Autenticação
│   │   ├── public.py        # Portal público
│   │   ├── admin.py         # Painel administrativo
│   │   ├── teacher.py       # Painel do professor
│   │   ├── student.py       # Painel do aluno
│   │   └── secretary.py     # Painel da secretaria
│   ├── templates/           # Templates HTML
│   │   ├── base.html        # Template base
│   │   ├── auth/            # Templates de autenticação
│   │   ├── public/          # Templates públicos
│   │   ├── admin/           # Templates admin
│   │   ├── teacher/         # Templates professor
│   │   ├── student/         # Templates aluno
│   │   └── secretary/       # Templates secretaria
│   ├── static/              # Arquivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/               # Utilitários
├── app.py                   # Ponto de entrada da aplicação
├── config.py                # Configurações
├── requirements.txt         # Dependências Python
└── .env.example            # Exemplo de variáveis de ambiente
```

## 🗄️ Modelos de Banco de Dados

### User
- Usuário base do sistema (Admin, Professor, Aluno, Secretaria)
- Autenticação com hash de senha
- Controle de permissões por papel (role)

### Teacher
- Perfil de professor vinculado ao usuário
- Instrumento e especialização
- Disponibilidades semanais

### Student
- Perfil de aluno vinculado ao usuário
- Instrumento de estudo
- Dados do responsável

### Room
- Salas para aulas
- Capacidade e equipamentos

### TeacherAvailability
- Disponibilidade semanal do professor
- Dias e horários recorrentes

### LessonSchedule
- Agendamento de aulas
- Relacionamento professor-aluno-sala
- Controle de status e tipo

### MakeupLesson
- Reposições de aulas
- Rastreamento de solicitações
- Sistema de aprovação

### Recital
- Eventos e apresentações
- Programação de recitais

### RecitalPerformance & RecitalParticipant
- Apresentações em recitais
- Participantes (alunos e professores)

### NewsPost
- Notícias e eventos do portal público

### TrialLesson
- Solicitações de aulas experimentais

## 👥 Níveis de Acesso

### Admin/Diretor
- Controle total do sistema
- Gestão de usuários
- Painel macro administrativo (visão global)
- Gerenciamento de salas e recursos
- Criação de recitais e eventos
- Publicação de notícias

### Secretaria
- Agendamento de aulas
- Gestão de reposições
- Visualização de agenda geral
- Acesso a solicitações de aula experimental

### Professor
- Definição de disponibilidade semanal
- Visualização da própria agenda
- Acesso a materiais e alunos

### Aluno
- Visualização de aulas agendadas
- Acesso a horários e materiais
- Portal pessoal

## 🚀 Funcionalidades Implementadas (MVP)

### ✅ Sistema de Autenticação
- Login/Logout com Flask-Login
- Registro de novos usuários
- Controle de sessão
- Proteção de rotas por papel

### ✅ Portal Público
- Landing page institucional
- Formulário de aula experimental
- Seção de notícias e eventos
- Design responsivo com Tailwind CSS

### ✅ Gestão de Usuários
- CRUD completo de usuários
- Perfis diferenciados por papel
- Gestão de professores e alunos

### ✅ Módulo de Agenda
- Professores definem disponibilidade semanal
- Secretaria agenda aulas
- Visualização por professor e aluno
- Controle de salas

### ✅ Sistema de Reposições
- Registro de solicitações de reposição
- Rastreamento de motivos
- Sistema de status (pendente/aprovado/recusado)
- Validação automática de conflitos

### ✅ Painel Macro Administrativo
- Visão global semanal
- Ocupação de salas
- Listagem de aulas por professor
- Dashboard com métricas

### ✅ Módulo de Recitais
- Criação de eventos
- Gestão de apresentações
- Sistema de participantes

### ✅ Interface com Tailwind CSS
- Design moderno e responsivo
- Componentes reutilizáveis
- Grid system para calendários
- Ícones Font Awesome

## 🔐 Acesso ao Sistema

### Usuários de Teste

#### Admin/Diretor
- **Email:** admin@solmaior.com
- **Senha:** admin123

#### Professor
- **Email:** professor@solmaior.com
- **Senha:** prof123
- Instrumento: Piano

#### Aluno
- **Email:** aluno@solmaior.com
- **Senha:** aluno123
- Instrumento: Violão

### Criando Novos Usuários
Use o painel administrativo após fazer login como admin. Os perfis específicos (Teacher, Student) são criados automaticamente ao selecionar o papel correspondente.

## 🌐 Endpoints Principais

### Públicos
- `/` - Landing page
- `/about` - Sobre a escola
- `/news` - Notícias
- `/trial-lesson` - Aula experimental
- `/auth/login` - Login
- `/auth/register` - Registro

### Admin
- `/admin/dashboard` - Dashboard
- `/admin/global-schedule` - Agenda global
- `/admin/users` - Gerenciar usuários
- `/admin/rooms` - Gerenciar salas
- `/admin/recitals` - Gerenciar recitais
- `/admin/news` - Gerenciar notícias
- `/admin/trial-lessons` - Solicitações

### Professor
- `/teacher/dashboard` - Dashboard
- `/teacher/availability` - Disponibilidade
- `/teacher/schedule` - Agenda

### Aluno
- `/student/dashboard` - Dashboard
- `/student/schedule` - Minhas aulas

### Secretaria
- `/secretary/dashboard` - Dashboard
- `/secretary/schedule` - Agenda semanal
- `/secretary/makeups` - Reposições

## 📝 Próximas Funcionalidades (Next Phase)

### Automações RPA com Celery + Redis
- Bot de lembrete diário de aulas
- Bot de detecção e marcação de faltas
- Bot de sugestão de reposições
- Bot de auditoria semanal
- Bot de otimização de agenda mensal

### Módulo Financeiro
- Controle de mensalidades
- Gestão de pagamentos
- Relatório de inadimplência
- Emissão de recibos em PDF

### Sistema de Documentos
- Upload de arquivos (contratos, partituras, PDFs)
- Armazenamento em cloud (AWS S3/Google Cloud)
- Biblioteca de materiais por instrumento
- Compartilhamento de áudios e vídeos

### Relatórios Avançados
- Taxa de ocupação de salas
- Horas lecionadas por professor
- Tempo ocioso e otimização
- KPIs de desempenho
- Dashboards analíticos

### Geração de PDFs
- Programas de recitais automáticos
- Certificados de participação
- Relatórios personalizados

## 🎨 Design e UX
- Interface moderna com Tailwind CSS
- Paleta de cores baseada em azul/roxo
- Componentes responsivos
- Ícones intuitivos
- Feedback visual para ações do usuário
- Sistema de notificações flash

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente
Configure o arquivo `.env` com base no `.env.example`:
- `DATABASE_URL` - URL do PostgreSQL (já configurado)
- `SECRET_KEY` - Chave secreta do Flask
- `JWT_SECRET_KEY` - Chave para tokens JWT
- Configurações de email (MAIL_*)

### Banco de Dados
O banco de dados é criado automaticamente ao iniciar a aplicação.
Dados iniciais (admin + salas) são criados via script Python.

## 🔒 Segurança

### Proteção CSRF
- Flask-WTF configurado para proteção contra Cross-Site Request Forgery
- Tokens CSRF automáticos em todos os formulários

### Validação de Dados
- Validação de campos obrigatórios
- Verificação de duplicidade de emails
- Tratamento de erros com rollback de transações
- Mensagens de erro informativas

### Autenticação
- Senhas hashadas com Werkzeug
- Controle de sessão com Flask-Login
- Proteção de rotas por papel (admin_required, teacher_required, etc.)

## 📊 Status do Projeto
✅ MVP Completo e Funcional
- Sistema de autenticação implementado com 4 níveis
- Criação automática de perfis (Teacher, Student)
- Portal público operacional
- Gestão acadêmica funcional
- Interface moderna e responsiva com Tailwind CSS
- Banco de dados configurado e populado
- Proteção CSRF ativada
- Validação de dados implementada
- Workflow funcionando

## 🔄 Histórico de Mudanças

### 2024-10-23 - v1.1 (Correções de Segurança)
- Adicionado Flask-WTF para proteção CSRF
- Implementada criação automática de perfis (Teacher/Student) ao criar usuário
- Adicionada validação robusta de dados nos formulários
- Tratamento de erros com rollback de transações
- Criados usuários de teste para todos os perfis

### 2024-10-23 - v1.0 (Lançamento Inicial)
- Criação inicial do projeto
- Implementação completa do MVP
- Configuração de todos os módulos principais
- Deploy e testes bem-sucedidos
