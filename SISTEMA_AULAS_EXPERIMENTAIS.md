# 🎵 Sistema de Aulas Experimentais - Sol Maior

## 📋 Visão Geral

Sistema completo de CRUD para gerenciar aulas experimentais com agendamento inteligente e notificações automáticas por email.

## ✅ Funcionalidades Implementadas

### 1. **Gestão de Solicitações**
- ✅ Visualizar todas as solicitações
- ✅ Filtrar por status (Pendente, Agendada, Concluída, Cancelada)
- ✅ Filtrar por instrumento
- ✅ Estatísticas em tempo real

### 2. **Agendamento de Aulas**
- ✅ Agendar aula experimental com:
  - Data e horário
  - Professor designado
  - Sala (opcional)
  - Duração (30, 60 ou 90 minutos)
  - Observações internas
- ✅ Reagendar aulas já agendadas
- ✅ Validação de campos obrigatórios

### 3. **Controle de Status**
- **Pendente**: Solicitação aguardando agendamento
- **Agendada**: Aula confirmada e email enviado
- **Concluída**: Aula realizada
- **Cancelada**: Aula cancelada (com motivo)

### 4. **Notificações Automáticas por Email**
- ✅ **Email de Confirmação**: Enviado automaticamente ao agendar
- ✅ **Email de Reagendamento**: Enviado ao modificar data/hora
- ✅ **Email de Cancelamento**: Enviado ao cancelar (com motivo)
- ✅ Reenviar confirmação manualmente
- ✅ Controle de envio (flag `confirmation_sent`)

### 5. **Detalhes do Email de Confirmação**

Cada email contém:
- 🎵 Instrumento escolhido
- 📅 Data do agendamento
- ⏰ Horário
- ⏱️ Duração da aula
- 👨‍🏫 Nome do professor
- 📍 Sala designada
- 📞 Telefone do cliente
- 📧 Email do cliente

### 6. **Segurança e Permissões**
- ✅ Acesso apenas para **Admin** e **Secretaria**
- ✅ Apenas Admin pode deletar solicitações
- ✅ Decorator `@admin_or_secretary_required`

---

## 🗂️ Estrutura de Arquivos

### Backend
```
app/routes/trial_lessons.py      # Rotas e lógica de negócio
app/models.py                     # Modelo TrialLesson atualizado
```

### Templates
```
app/templates/trial_lessons/
├── index.html                    # Lista de solicitações
└── view.html                     # Detalhes e agendamento
```

### Scripts
```
migrate_trial_lessons.py          # Migração do banco de dados
```

---

## 🔧 Novos Campos do Modelo

```python
class TrialLesson(db.Model):
    # Campos existentes
    id, full_name, email, phone, instrument
    preferred_date, preferred_time, message
    status, created_at, updated_at
    
    # NOVOS CAMPOS (v2.2)
    scheduled_date          # Data confirmada
    scheduled_time          # Hora confirmada
    assigned_teacher_id     # Professor designado
    room_id                 # Sala
    duration_minutes        # Duração (padrão: 60min)
    confirmation_sent       # Email enviado?
    notes                   # Observações internas
```

---

## 🚀 Como Usar

### 1. Executar Migração do Banco de Dados

```bash
python migrate_trial_lessons.py
```

Isso irá adicionar os novos campos à tabela `trial_lessons`.

### 2. Reiniciar o Servidor

```bash
python app.py
```

### 3. Acessar o Sistema

**Admin**:
- Acesse: http://localhost:5000/admin/dashboard
- Clique em "Aulas Experimentais"

**Secretaria**:
- Acesse: http://localhost:5000/secretary/dashboard
- Clique em "Aulas Experimentais"

**URL Direta**:
- http://localhost:5000/trial-lessons

---

## 📝 Fluxo de Trabalho

### Cenário 1: Cliente Solicita Aula Experimental
1. Cliente preenche formulário no site público
2. Solicitação é criada com status **Pendente**
3. Admin/Secretaria visualiza na lista

### Cenário 2: Agendar Aula
1. Acesse "Ver Detalhes" da solicitação
2. Preencha formulário de agendamento:
   - Data *
   - Horário *
   - Professor *
   - Sala (opcional)
   - Duração
   - Observações
3. Clique "Confirmar Agendamento"
4. **Email automático é enviado ao cliente**
5. Status muda para **Agendada**

### Cenário 3: Reagendar Aula
1. Acesse aula com status "Agendada"
2. No formulário "Reagendar Aula":
   - Nova data
   - Novo horário
   - Observações
3. Clique "Reagendar e Notificar Cliente"
4. **Email de reagendamento é enviado**

### Cenário 4: Marcar Como Concluída
1. Após a aula ser realizada
2. Clique "Marcar Concluída"
3. Status muda para **Concluída**

### Cenário 5: Cancelar Aula
1. Clique "Cancelar Aula"
2. Informe o motivo
3. **Email de cancelamento é enviado**
4. Status muda para **Cancelada**

---

## 📧 Configuração de Email

Certifique-se de ter o email configurado no `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

**Testar email**:
```bash
flask test-email
```

---

## 🎨 Interface do Usuário

### Tela Principal (index.html)
- **Cards de Estatísticas**: Pendentes, Agendadas, Concluídas, Canceladas
- **Filtros**: Por status e instrumento
- **Lista de Solicitações**: 
  - Informações do cliente
  - Badge de status colorido
  - Indicador de email enviado
  - Botões de ação

### Tela de Detalhes (view.html)
- **Coluna Esquerda**:
  - Informações completas do cliente
  - Preferências do cliente
  - Mensagem original
  - Agendamento atual (se houver)
  - Formulário de reagendamento
  
- **Coluna Direita**:
  - Formulário de agendamento (se pendente)
  - Ações rápidas
  - Botões de marcar concluída/cancelar

---

## 🎯 Casos de Uso

### Caso 1: Solicitação Pendente
```
Cliente solicita → Status: Pendente → Admin agenda → Email enviado → Status: Agendada
```

### Caso 2: Mudança de Data
```
Aula agendada → Cliente pede nova data → Admin reagenda → Email reenviado → Cliente confirmado
```

### Caso 3: Aula Realizada
```
Aula agendada → Cliente comparece → Admin marca concluída → Status: Concluída
```

### Caso 4: Cancelamento
```
Aula agendada → Cliente cancela → Admin cancela com motivo → Email enviado → Status: Cancelada
```

---

## 📊 Estatísticas e Filtros

### Dashboard
- Total de aulas pendentes
- Total de aulas agendadas
- Total de aulas concluídas
- Total de aulas canceladas

### Filtros Disponíveis
- **Status**: Todos, Pendentes, Agendadas, Concluídas, Canceladas
- **Instrumento**: Todos os instrumentos registrados

---

## 🔒 Segurança

### Controle de Acesso
- ✅ Apenas Admin e Secretaria podem acessar
- ✅ Apenas Admin pode deletar solicitações
- ✅ CSRF Protection ativo
- ✅ Login obrigatório

### Validações
- ✅ Campos obrigatórios validados
- ✅ Formato de data e hora validado
- ✅ Professor deve existir e estar ativo
- ✅ Sala deve existir e estar ativa

---

## 🐛 Troubleshooting

### Email não está sendo enviado
1. Verifique configuração no `.env`
2. Execute: `flask test-email`
3. Para Gmail, use Senha de App
4. Verifique logs no console

### Erro ao agendar
1. Verifique se há professores ativos
2. Verifique se os campos obrigatórios estão preenchidos
3. Veja o erro específico no flash message

### Campos não aparecem no banco
1. Execute: `python migrate_trial_lessons.py`
2. Reinicie o servidor
3. Verifique se migração foi bem-sucedida

---

## 📈 Melhorias Futuras (Sugestões)

- [ ] Integração com Google Calendar
- [ ] Whatsapp notifications
- [ ] Lembretes automáticos 24h antes
- [ ] Confirmação de presença pelo cliente
- [ ] Avaliação da aula experimental
- [ ] Conversão para matrícula regular
- [ ] Dashboard de conversão (leads → alunos)
- [ ] Relatório mensal de aulas experimentais

---

## 📞 Suporte

**Dúvidas sobre implementação?**
- Consulte este documento
- Veja comentários no código
- Verifique templates HTML

---

## ✨ Resumo das Vantagens

1. **Automatização**: Emails enviados automaticamente
2. **Organização**: Status claro e filtros eficientes
3. **Profissionalismo**: Emails bem formatados
4. **Rastreabilidade**: Histórico completo de cada solicitação
5. **Facilidade**: Interface intuitiva para admin/secretaria
6. **Segurança**: Controle de acesso e validações

---

**Sistema de Aulas Experimentais v1.0**
*Implementado em 26/10/2025*
*Escola de Música Sol Maior* 🎵
