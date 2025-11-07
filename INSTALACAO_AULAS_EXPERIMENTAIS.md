# 🚀 Instalação Rápida - Sistema de Aulas Experimentais

## ⚡ Passos de Instalação

### 1️⃣ Pare o Servidor
```bash
# Pressione Ctrl+C no terminal onde o servidor está rodando
```

### 2️⃣ Execute a Migração
```bash
python migrate_trial_lessons.py
```

**Responda "s" quando perguntado**

Você verá:
```
✓ Campo 'scheduled_date' adicionado
✓ Campo 'scheduled_time' adicionado
✓ Campo 'assigned_teacher_id' adicionado
✓ Campo 'room_id' adicionado
✓ Campo 'duration_minutes' adicionado
✓ Campo 'confirmation_sent' adicionado
✓ Campo 'notes' adicionado
✓ Índice criado
✅ Migração concluída com sucesso!
```

### 3️⃣ Reinicie o Servidor
```bash
python app.py
```

### 4️⃣ Acesse o Sistema
Faça login como **admin** ou **secretaria** e acesse:

**Opção 1**: Menu do Dashboard
- Dashboard → Aulas Experimentais

**Opção 2**: URL Direta
```
http://localhost:5000/trial-lessons
```
ou
```
http://192.168.100.10:5000/trial-lessons
```

---

## ✅ Verificar Instalação

### Teste 1: Acessar Lista
1. Acesse `/trial-lessons`
2. Deve mostrar lista de aulas experimentais
3. Deve mostrar estatísticas no topo

### Teste 2: Agendar Aula
1. Clique em "Ver Detalhes" de uma solicitação pendente
2. Preencha formulário de agendamento
3. Clique "Confirmar Agendamento"
4. Verifique se email foi enviado

### Teste 3: Email
```bash
flask test-email
```
Digite um email de teste e verifique se recebe.

---

## 🎯 Funcionalidades Disponíveis Após Instalação

✅ Visualizar solicitações de aulas experimentais
✅ Agendar aulas com professor e sala
✅ Enviar email automático de confirmação
✅ Reagendar aulas
✅ Marcar como concluída
✅ Cancelar com motivo
✅ Filtrar por status e instrumento
✅ Ver estatísticas em tempo real

---

## 📧 Configurar Email (Se ainda não fez)

Edite `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=pageupsistemas@gmail.com
MAIL_PASSWORD=@Pageup#23
```

---

## 🐛 Problemas Comuns

### "No such column: trial_lessons.scheduled_date"
**Solução**: Execute a migração novamente
```bash
python migrate_trial_lessons.py
```

### "404 Not Found" ao acessar /trial-lessons
**Solução**: Reinicie o servidor
```bash
# Pare com Ctrl+C
python app.py
```

### Email não está sendo enviado
**Solução**: 
1. Verifique `.env`
2. Execute `flask test-email`
3. Para Gmail, use "Senha de App"

---

## 📝 Próximos Passos

1. ✅ Instalar sistema (você está aqui)
2. Testar agendamento de uma aula
3. Verificar email recebido
4. Treinar equipe admin/secretaria
5. Começar a usar em produção

---

## 💡 Dicas de Uso

- **Pendentes**: Solicitações aguardando agendamento
- **Agendadas**: Aulas confirmadas (email enviado)
- **Concluídas**: Aulas já realizadas
- **Canceladas**: Aulas canceladas (com motivo)

Use os filtros para organizar melhor as solicitações!

---

**Instalação completa!** 🎉
Agora você pode gerenciar aulas experimentais de forma profissional.
