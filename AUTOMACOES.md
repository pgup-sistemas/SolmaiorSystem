# Sistema de Automações - Solmaior

## Visão Geral

O sistema possui automações inteligentes para reduzir trabalho manual e melhorar a comunicação com alunos e professores.

## Funcionalidades Implementadas

### 1. Lembretes de Aula (24h antes)
- **Frequência**: Diária (executar às 8h da manhã)
- **Funcionamento**:
  - Busca todas as aulas agendadas para o dia seguinte
  - Envia email para aluno e professor
  - Inclui informações: data, horário, sala, professor/aluno

### 2. Marcação Automática de Faltas
- **Frequência**: Diária (executar às 8h da manhã)
- **Funcionamento**:
  - Busca aulas do dia anterior não confirmadas pelo professor
  - Marca automaticamente como falta
  - Envia notificação ao aluno

### 3. Lembretes de Pagamento
- **Frequência**: Diária (executar às 9h da manhã)
- **Funcionamento**:
  - 3 dias antes do vencimento: aviso antecipado
  - No dia do vencimento: lembrete urgente
  - 3 dias após vencimento: aviso de atraso

### 4. Processamento de Notificações
- **Frequência**: A cada hora
- **Funcionamento**:
  - Processa até 100 notificações pendentes
  - Envia emails agendados
  - Registra falhas e tenta reenviar (até 3 tentativas)

## Como Usar

### Método 1: Comandos Flask CLI

```bash
# Tarefas diárias (lembretes + faltas)
flask run-daily-tasks

# Tarefas horárias (notificações)
flask run-hourly-tasks

# Testar configuração de email
flask test-email
```

### Método 2: Script Python

```bash
# Tarefas diárias
python run_tasks.py daily

# Tarefas horárias
python run_tasks.py hourly

# Todas as tarefas
python run_tasks.py all
```

### Método 3: Agendamento com Cron

Edite o crontab:
```bash
crontab -e
```

Adicione as linhas (ajuste o caminho do projeto):
```cron
# Tarefas horárias
0 * * * * cd /caminho/do/projeto && python3 run_tasks.py hourly >> /var/log/solmaior/hourly.log 2>&1

# Tarefas diárias às 8h
0 8 * * * cd /caminho/do/projeto && python3 run_tasks.py daily >> /var/log/solmaior/daily.log 2>&1
```

## Configuração de Email

Edite o arquivo `.env` com suas credenciais:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

**Nota**: Para Gmail, você precisa gerar uma "Senha de App" nas configurações de segurança da conta Google.

## Tipos de Notificações

| Tipo | Descrição | Destinatário |
|------|-----------|--------------|
| `lesson_reminder` | Lembrete de aula 24h antes | Aluno e Professor |
| `auto_absence` | Falta registrada automaticamente | Aluno |
| `absence_alert` | Falta registrada pelo professor | Aluno |
| `payment_upcoming` | Pagamento vence em 3 dias | Aluno |
| `payment_due_today` | Pagamento vence hoje | Aluno |
| `payment_overdue` | Pagamento em atraso | Aluno |
| `makeup_approved` | Reposição aprovada | Aluno |
| `makeup_rejected` | Reposição rejeitada | Aluno |
| `waitlist_matched` | Vaga disponível na fila de espera | Aluno |

## Monitoramento

As notificações são registradas na tabela `scheduled_notifications` com os seguintes status:

- **pending**: Aguardando envio
- **sent**: Enviada com sucesso
- **failed**: Falha no envio
- **cancelled**: Cancelada

Logs podem ser consultados em:
- `/var/log/solmaior/hourly.log` - Tarefas horárias
- `/var/log/solmaior/daily.log` - Tarefas diárias

## Troubleshooting

### Emails não estão sendo enviados
1. Verifique as credenciais no `.env`
2. Execute `flask test-email` para testar
3. Verifique os logs de erro
4. Para Gmail, certifique-se de usar Senha de App

### Notificações ficam em "pending"
1. Verifique se o cron job está rodando
2. Execute manualmente: `flask run-hourly-tasks`
3. Verifique logs de erro na tabela `scheduled_notifications`

### Faltas não estão sendo marcadas
1. Verifique se o cron job diário está configurado
2. Execute manualmente: `flask run-daily-tasks`
3. Verifique se as aulas têm o status correto (`scheduled`)

## Customização

Para customizar mensagens de email, edite o arquivo `app/tasks.py`:

```python
def create_lesson_reminders():
    # Edite as mensagens aqui
    message = f'Sua mensagem personalizada...'
```

## Desempenho

- Lembretes de aula: ~100ms por aula
- Marcação de faltas: ~50ms por aula
- Processamento de notificações: até 100 por execução
- Recomendado: servidor com pelo menos 512MB RAM
