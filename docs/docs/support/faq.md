# ❓ Perguntas Frequentes (FAQ)

!!! info "Dúvidas Mais Comuns"

    Encontre respostas rápidas para as perguntas mais frequentes sobre o Sistema Sol Maior.

## 🚀 Instalação e Configuração

### Como instalar o sistema?

**Resposta**: O Sistema Sol Maior pode ser instalado de 3 formas:

1. **Automática** (Recomendada): Execute `./install.sh` no servidor
2. **Manual**: Siga o [guia de instalação](../install/installation.md)
3. **Docker**: Use `docker-compose up` para desenvolvimento

!!! tip "Pré-requisitos"
    Certifique-se de ter Python 3.8+, PostgreSQL e Redis instalados.

### Quais são os requisitos mínimos?

**Requisitos de Hardware:**
- CPU: 2 cores
- RAM: 4 GB
- Armazenamento: 50 GB SSD
- Sistema: Linux Ubuntu 20.04+

**Software:**
- Python 3.8 ou superior
- PostgreSQL 15+ ou MySQL 8.0+
- Redis 7.0+
- Nginx (opcional para produção)

### Como configurar o banco de dados?

```bash
# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE solmaior_db;
CREATE USER solmaior WITH PASSWORD 'sua_senha';
GRANT ALL ON DATABASE solmaior_db TO solmaior;
\q

# Configurar no sistema
export DATABASE_URL="postgresql://solmaior:senha@localhost/solmaior_db"
```

### Como fazer backup dos dados?

```bash
# Backup completo
pg_dump solmaior_db > backup_$(date +%Y%m%d).sql

# Backup automático (crontab)
0 2 * * * pg_dump solmaior_db > /backup/daily_$(date +%Y%m%d).sql

# Restauração
psql solmaior_db < backup_20250101.sql
```

## 👤 Gestão de Usuários

### Como criar um novo usuário?

1. Acesse **Admin → Usuários → Novo Usuário**
2. Preencha os dados básicos (nome, email, perfil)
3. Defina uma senha temporária
4. Configure permissões específicas se necessário
5. Clique em **Salvar**

!!! warning "Importante"
    Oriente o usuário a alterar a senha no primeiro acesso.

### Quais são os perfis de usuário disponíveis?

| Perfil | Descrição | Permissões |
|--------|-----------|------------|
| **Admin** | Controle total | Tudo |
| **Secretaria** | Gestão operacional | Alunos, agendamentos, financeiro básico |
| **Professor** | Ensino | Suas aulas, alunos |
| **Aluno** | Portal pessoal | Suas informações |

### Como redefinir senha de usuário?

**Para administradores:**
1. Acesse **Admin → Usuários**
2. Localize o usuário
3. Clique em **Editar → Alterar Senha**
4. Defina nova senha

**Para usuários comuns:**
- Use o link "Esqueci minha senha" na tela de login
- Sistema envia email com link de redefinição

## 🎵 Agendamento de Aulas

### Como agendar uma aula?

1. Acesse **Secretaria → Agenda**
2. Clique em **Nova Aula**
3. Selecione **Professor**, **Aluno** e **Sala**
4. Escolha **Data** e **Horário**
5. Adicione **Observações** se necessário
6. Clique em **Agendar**

!!! tip "Dicas"
    - Sistema valida conflitos automaticamente
    - Verifica disponibilidade do professor
    - Sugere horários alternativos se necessário

### Como funciona o sistema de reposições?

**Automático:**
- Sistema detecta aulas canceladas
- Gera sugestões de horários automaticamente
- Notifica aluno e professor

**Manual:**
1. Acesse **Secretaria → Reposições**
2. Clique em **Nova Reposição**
3. Selecione aula original
4. Escolha novo horário
5. Aprove ou rejeite solicitação

### Como gerenciar a fila de espera?

1. **Adicionar aluno**: **Secretaria → Fila de Espera → Adicionar**
2. **Definir prioridade**: Sistema ordena por data de entrada
3. **Atender demanda**: Quando surge vaga, notificar primeiro da fila
4. **Remover da fila**: Após agendamento ou cancelamento

## 💰 Sistema Financeiro

### Como configurar mensalidades?

1. Acesse **Financeiro → Planos**
2. Clique em **Novo Plano**
3. Defina:
   - Nome (ex: "Individual - Piano")
   - Valor mensal
   - Número de aulas incluídas
   - Descrição

!!! example "Planos Sugeridos"
    - **Individual**: R$ 150/mês (4 aulas)
    - **Duo**: R$ 100/mês (4 aulas compartilhadas)
    - **Grupo**: R$ 80/mês (4 aulas coletivas)

### Como configurar descontos automáticos?

**Desconto por frequência:**
- 100% presença: 10% desconto
- 95% presença: 5% desconto
- Sistema calcula automaticamente mensalmente

**Outros descontos:**
- Irmãos: 15% para segundo filho
- Pagamento antecipado: 5% desconto
- Campanhas especiais: configuráveis

### Como integrar gateways de pagamento?

```python
# config.py
PAYMENT_GATEWAYS = {
    'mercado_pago': {
        'enabled': True,
        'access_token': 'APP_USR-...',
        'public_key': 'APP_USR-...'
    },
    'pagseguro': {
        'enabled': False,
        'email': 'seu@email.com',
        'token': 'seu_token'
    }
}
```

!!! warning "Produção vs Sandbox"
    Use credenciais de produção apenas em ambiente de produção!

## 📧 Notificações e Comunicação

### Como configurar emails?

```python
# config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'seu@email.com'
MAIL_PASSWORD = 'sua_senha_app'
```

### Quais tipos de notificação existem?

- **Lembretes de aula**: 24h antes
- **Alertas de pagamento**: Vencimento, atraso
- **Confirmações**: Agendamento, cancelamento
- **Recitais**: Convites, confirmações
- **Sistema**: Avisos importantes

### Como personalizar templates?

1. Acesse **Admin → Notificações → Templates**
2. Selecione template desejado
3. Edite conteúdo usando variáveis:
   - `{{student_name}}` - Nome do aluno
   - `{{lesson_date}}` - Data da aula
   - `{{teacher_name}}` - Nome do professor

## 📊 Relatórios e Analytics

### Quais relatórios estão disponíveis?

| Relatório | Frequência | Conteúdo |
|-----------|------------|----------|
| **Financeiro** | Diário/Mensal | Receitas, pagamentos, inadimplência |
| **Acadêmico** | Semanal | Aulas realizadas, frequência |
| **Alunos** | Mensal | Novos alunos, evasão |
| **Professores** | Trimestral | Performance, ocupação |

### Como exportar dados?

1. Acesse **Relatórios**
2. Selecione período e filtros
3. Escolha formato: PDF, Excel ou CSV
4. Clique em **Exportar**

### Como funciona o dashboard preditivo?

**Indicadores calculados automaticamente:**
- **Risco de evasão**: Baseado em faltas e pagamentos
- **Previsão de receita**: Próximos 30 dias
- **Ocupação de salas**: Taxa de utilização
- **Demanda não atendida**: Tamanho da fila de espera

## 🎭 Gestão de Recitais

### Como criar um recital?

1. Acesse **Admin → Recitais → Novo Recital**
2. Preencha:
   - Título e descrição
   - Data e horário
   - Local
   - Tipo (solo, grupo, concerto)

### Como gerenciar inscrições?

1. **Publicar recital**: Tornar visível para alunos
2. **Receber inscrições**: Alunos se inscrevem online
3. **Organizar programação**: Sistema monta ordem automaticamente
4. **Enviar convites**: Notificações por email

### Como gerar certificados?

**Automático:**
- Sistema gera após evento
- Design profissional padrão
- Download individual pelos participantes

**Personalizado:**
1. Acesse **Recital → Participantes**
2. Selecione participante
3. Clique em **Gerar Certificado**
4. Customize se necessário

## 🔧 Solução de Problemas

### Sistema lento - o que fazer?

**Verificações:**
1. **CPU/Memória**: `htop` ou `top`
2. **Banco de dados**: Verificar conexões ativas
3. **Redis**: `redis-cli info`
4. **Logs**: Verificar erros em logs/app.log

**Otimizações:**
- Aumentar recursos do servidor
- Otimizar consultas SQL
- Configurar cache Redis
- Implementar CDN para assets

### Emails não estão sendo enviados?

**Verificações:**
1. **Configuração SMTP**: Verificar credenciais
2. **Firewall**: Porta 587/465 liberada?
3. **Logs**: Verificar erros de envio
4. **Spam**: Email foi para caixa de spam?

**Soluções:**
- Usar provedores como SendGrid ou Amazon SES
- Verificar configurações de DNS (SPF, DKIM)
- Testar com ferramentas como Mail-Tester

### Erro de conexão com banco?

```bash
# Testar conexão
psql -h localhost -U solmaior -d solmaior_db

# Verificar serviço
sudo systemctl status postgresql

# Logs de erro
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Como restaurar backup?

```bash
# Parar aplicação
sudo systemctl stop solmaior

# Restaurar banco
psql solmaior_db < backup.sql

# Restaurar arquivos (se necessário)
tar -xzf files_backup.tar.gz -C /var/www/solmaior/

# Reiniciar aplicação
sudo systemctl start solmaior
```

## 🔐 Segurança

### Como proteger o sistema?

**Medidas básicas:**
- Manter sistema atualizado
- Usar senhas fortes
- Configurar firewall (UFW)
- Habilitar HTTPS com Let's Encrypt

**Configurações avançadas:**
- Configurar fail2ban para proteção SSH
- Usar VPN para acesso remoto
- Implementar 2FA para admins
- Monitorar logs regularmente

### Como configurar backup automático?

```bash
# Instalar ferramentas
sudo apt install duplicity

# Configurar backup diário
crontab -e
# Adicionar:
0 2 * * * duplicity /var/www/solmaior file:///backup/solmaior

# Backup para nuvem
0 3 * * * duplicity /var/www/solmaior s3://bucket/backup
```

## 📞 Suporte e Contato

### Como obter suporte?

**Canais oficiais:**
- 📧 **Email**: suporte@solmaior.com.br
- 📱 **WhatsApp**: (11) 99999-9999
- 📋 **Chat online**: solmaior.com.br/suporte
- 📚 **Documentação**: docs.solmaior.com.br

**Horário de atendimento:**
- Segunda a Sexta: 8h às 18h
- Sábado: 8h às 12h
- Domingo: Emergências apenas

### Planos de suporte disponíveis?

| Plano | SLA | Canais | Valor |
|-------|-----|---------|-------|
| **Básico** | 48h | Email | Gratuito |
| **Profissional** | 24h | Email + Chat | R$ 199/mês |
| **Enterprise** | 4h | Telefone + Chat | R$ 499/mês |

---

!!! tip "Não encontrou sua dúvida?"

    **Consulte a documentação completa** ou **entre em contato conosco**. Estamos aqui para ajudar!

!!! info "Documentação atualizada"

    Esta FAQ é atualizada regularmente. Última atualização: Janeiro 2025.