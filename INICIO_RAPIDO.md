# 🚀 Início Rápido - Sistema Solmaior v2.2

## Checklist de Ativação

### ✅ Passo 1: Migrar Banco de Dados (OBRIGATÓRIO)
```bash
python migrate_new_features.py
```
**O que faz**: Adiciona novas tabelas e campos necessários para as funcionalidades v2.2

---

### ✅ Passo 2: Configurar Email (OBRIGATÓRIO)

Edite o arquivo `.env` (ou crie se não existir):
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

**Para Gmail**:
1. Acesse: https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Gere uma "Senha de app" em "Senhas de app"
4. Use essa senha no `MAIL_PASSWORD`

**Testar**:
```bash
flask test-email
```

---

### ✅ Passo 3: Iniciar o Sistema
```bash
python app.py
```
ou
```bash
flask run
```

Acesse: http://localhost:5000

---

## 🎯 Acessando as Novas Funcionalidades

### PROFESSOR
```
Login como professor → Menu:
├── 📚 Minhas Aulas         (/teacher/lessons)
│   ├── Confirmar presença/falta
│   ├── Filtrar por período
│   └── Adicionar notas da aula
├── 👨‍🎓 Meus Alunos        (/teacher/students)
│   ├── Ver estatísticas de frequência
│   └── Histórico completo por aluno
└── 📊 Dashboard            (/teacher/dashboard)
```

**Funcionalidades**:
- ✅ Confirmar presença: Presente, Ausente, Atrasado, Justificado
- ✅ Adicionar notas: Conteúdo, lição de casa, progresso
- ✅ Ver histórico completo de cada aluno

---

### FINANCEIRO/ADMIN
```
Login como admin → Financeiro → Menu:
├── 💰 Pagamentos           (/financial/payments)
│   ├── Aplicar desconto manual
│   └── Criar parcelamento (2-12x)
├── 🎁 Descontos            (/financial/discounts)
│   ├── Criar novos descontos
│   ├── Ativar/desativar
│   └── Configurar aplicação automática
└── 📊 Desconto Frequência  (/financial/frequency-discounts)
    ├── Ver alunos elegíveis
    └── Aplicar descontos automáticos
```

**Funcionalidades**:
- ✅ Descontos configuráveis (% ou valor fixo)
- ✅ Parcelamento até 12x
- ✅ Desconto automático por frequência (100%=10%, 95%=5%, 90%=3%)

---

### SECRETARIA
```
Login como secretaria → Menu:
├── 📅 Agenda Global        (/secretary/global-schedule)
│   ├── Ver todas as aulas
│   ├── Filtrar: data, professor, sala
│   └── Identificar conflitos
├── 🔄 Reposições           (/secretary/makeups)
│   ├── Aprovar com agendamento
│   └── Rejeitar com motivo
└── ⏳ Fila de Espera       (/secretary/waitlist)
    ├── Adicionar alunos
    ├── Marcar vaga disponível
    └── Gerenciar prioridades
```

**Funcionalidades**:
- ✅ Aprovar/rejeitar reposições com notificação automática
- ✅ Agenda centralizada com filtros
- ✅ Fila de espera com prioridades e expiração

---

## 🤖 Configurar Automações (OPCIONAL mas RECOMENDADO)

### Testar Manualmente Primeiro
```bash
# Criar lembretes de aula (24h antes)
flask run-daily-tasks

# Processar notificações pendentes
flask run-hourly-tasks
```

### Configurar Cron (Linux/Mac)
```bash
crontab -e
```

Adicione:
```cron
# Processar notificações a cada hora
0 * * * * cd /caminho/completo/do/projeto && /usr/bin/python3 run_tasks.py hourly >> /tmp/solmaior-hourly.log 2>&1

# Tarefas diárias às 8h (lembretes + faltas)
0 8 * * * cd /caminho/completo/do/projeto && /usr/bin/python3 run_tasks.py daily >> /tmp/solmaior-daily.log 2>&1
```

**Importante**: Substitua `/caminho/completo/do/projeto` pelo caminho real!

---

## 📧 Tipos de Notificações Automáticas

| Notificação | Quando | Destinatário |
|-------------|--------|--------------|
| 📚 Lembrete de Aula | 24h antes | Aluno + Professor |
| ❌ Falta Automática | Aula não confirmada | Aluno |
| ✅ Falta Registrada | Professor marca | Aluno |
| 💰 Pagamento (3d antes) | 3 dias antes vencimento | Aluno |
| 💰 Pagamento (hoje) | No vencimento | Aluno |
| 💰 Pagamento (atraso) | 3 dias após vencimento | Aluno |
| 🔄 Reposição Aprovada | Ao aprovar | Aluno |
| 🔄 Reposição Rejeitada | Ao rejeitar | Aluno |
| ⏳ Vaga Disponível | Fila de espera | Aluno |

---

## 🔍 Verificar se Está Funcionando

### 1. Ver Notificações Agendadas (Banco de Dados)
No terminal Python:
```python
from app import create_app
from app.models import ScheduledNotification
app = create_app()
with app.app_context():
    notifications = ScheduledNotification.query.all()
    for n in notifications:
        print(f"{n.notification_type}: {n.status} - {n.recipient_email}")
```

### 2. Ver Logs
```bash
# Logs das tarefas horárias
tail -f /tmp/solmaior-hourly.log

# Logs das tarefas diárias
tail -f /tmp/solmaior-daily.log
```

### 3. Testar Fluxo Completo

**Teste de Lembrete de Aula**:
1. Crie uma aula para amanhã
2. Execute: `flask run-daily-tasks`
3. Execute: `flask run-hourly-tasks`
4. Verifique o email do aluno

**Teste de Falta Automática**:
1. Crie uma aula para ontem (use o banco direto ou admin)
2. NÃO confirme a presença
3. Execute: `flask run-daily-tasks`
4. Verifique: aula deve estar com status "absent"
5. Aluno deve receber email

**Teste de Desconto por Frequência**:
1. Acesse: /financial/frequency-discounts
2. Clique "Aplicar" em algum desconto elegível
3. Verifique o pagamento do aluno

---

## ❓ Troubleshooting Rápido

### Emails não estão sendo enviados
```bash
# 1. Testar configuração
flask test-email

# 2. Verificar variáveis de ambiente
python -c "from app import create_app; app=create_app(); print(app.config['MAIL_USERNAME'])"

# 3. Ver notificações com erro
# No Python shell:
from app.models import ScheduledNotification
ScheduledNotification.query.filter_by(status='failed').all()
```

### Notificações ficam em "pending"
```bash
# Executar processamento manual
flask run-hourly-tasks

# Verificar se tem erro no log
tail -f /tmp/solmaior-hourly.log
```

### Migração não funcionou
```bash
# Executar novamente (é seguro)
python migrate_new_features.py

# Verificar se tabelas foram criadas
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print(db.engine.table_names())"
```

---

## 📚 Documentação Completa

- **IMPLEMENTACAO_V2.2_COMPLETA.md**: Documentação detalhada de tudo
- **AUTOMACOES.md**: Guia completo das automações
- **crontab.example**: Exemplo de configuração cron

---

## 🎉 Tudo Pronto!

Agora você tem um sistema completo com:
- ✅ Controle de presença e notas pelos professores
- ✅ Sistema financeiro avançado com descontos
- ✅ Gestão profissional da secretaria
- ✅ Automações inteligentes

**Dúvidas?** Consulte a documentação ou os comentários no código-fonte.

---

**Sistema Solmaior v2.2** 🎵
*Desenvolvido com excelência*
