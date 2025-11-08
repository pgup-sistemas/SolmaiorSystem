# 🚀 Instalação do Sistema

!!! info "Guia de Instalação Completo"

    Siga este guia passo-a-passo para instalar o Sistema Sol Maior em seu ambiente.

## 📦 Método 1: Instalação Automática (Recomendado)

### Usando o Script de Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/solmaior/SolmaiorSystem-1.git
cd SolmaiorSystem-1

# 2. Executar script de instalação
chmod +x install.sh
sudo ./install.sh

# 3. Seguir as instruções na tela
```

O script irá automaticamente:
- ✅ Instalar dependências do sistema
- ✅ Configurar banco de dados
- ✅ Criar usuário administrador
- ✅ Configurar serviços (Nginx, Redis)
- ✅ Gerar certificados SSL (opcional)

### O que o script faz:

```bash
#!/bin/bash
# Script de instalação automática

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências
apt install -y python3 python3-pip postgresql redis-server nginx

# Configurar PostgreSQL
sudo -u postgres createuser --createdb solmaior
sudo -u postgres createdb -O solmaior solmaior_db

# Instalar dependências Python
pip install -r requirements.txt

# Executar migrações
flask db upgrade

# Criar usuário admin
python init_admin.py

# Configurar Nginx
cp nginx.conf /etc/nginx/sites-available/solmaior
ln -s /etc/nginx/sites-available/solmaior /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "Instalação concluída! Acesse http://seu-servidor"
```

## 🛠️ Método 2: Instalação Manual

### Passo 1: Preparar o Ambiente

```bash
# Criar diretório do projeto
mkdir -p /var/www/solmaior
cd /var/www/solmaior

# Clonar repositório
git clone https://github.com/solmaior/SolmaiorSystem-1.git .
```

### Passo 2: Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # Para produção
```

### Passo 3: Configurar Banco de Dados

#### PostgreSQL
```bash
# Criar usuário e banco
sudo -u postgres psql

CREATE USER solmaior WITH PASSWORD 'sua_senha_segura';
CREATE DATABASE solmaior_db OWNER solmaior;
GRANT ALL PRIVILEGES ON DATABASE solmaior_db TO solmaior;
\q
```

#### MySQL (Alternativo)
```bash
# Criar banco e usuário
mysql -u root -p

CREATE DATABASE solmaior_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'solmaior'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON solmaior_db.* TO 'solmaior'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Passo 4: Configurar Aplicação

```bash
# Copiar arquivo de configuração
cp config.py.example config.py

# Editar configurações
nano config.py
```

Conteúdo do `config.py`:

```python
import os

# Configurações básicas
SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-segura-aqui'
DEBUG = False

# Banco de dados
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://solmaior:sua_senha_segura@localhost/solmaior_db'

# Redis
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# Email
MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'apikey'
MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')

# Gateways de pagamento
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get('MERCADO_PAGO_ACCESS_TOKEN')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
```

### Passo 5: Executar Migrações

```bash
# Definir variável de ambiente
export FLASK_APP=app.py

# Executar migrações
flask db upgrade

# Criar usuário administrador
python init_admin.py
```

### Passo 6: Configurar Servidor Web

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/solmaior
server {
    listen 80;
    server_name seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static {
        alias /var/www/solmaior/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/solmaior /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### Passo 7: Configurar Gunicorn

```bash
# Criar arquivo de serviço systemd
sudo nano /etc/systemd/system/solmaior.service
```

Conteúdo do arquivo de serviço:

```ini
[Unit]
Description=Gunicorn instance to serve Sol Maior
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/solmaior
Environment="PATH=/var/www/solmaior/venv/bin"
ExecStart=/var/www/solmaior/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar serviço
sudo systemctl start solmaior
sudo systemctl enable solmaior

# Verificar status
sudo systemctl status solmaior
```

## 🐳 Método 3: Docker (Desenvolvimento)

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://solmaior:password@db/solmaior_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: gunicorn --bind 0.0.0.0:8000 app:app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=solmaior
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=solmaior_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

```bash
# Executar com Docker Compose
docker-compose up -d

# Executar migrações
docker-compose exec web flask db upgrade

# Criar admin
docker-compose exec web python init_admin.py
```

## 🔧 Configuração Inicial

### Primeiro Acesso

1. **Acesse o sistema**: `http://seu-dominio.com`
2. **Login inicial**:
   - Usuário: `admin@solmaior.com`
   - Senha: `admin123` (altere imediatamente)

### Configurações Essenciais

```python
# No painel admin, configure:

# 1. Informações da escola
- Nome da instituição
- Endereço e contato
- Logo e identidade visual

# 2. Políticas acadêmicas
- Duração padrão das aulas
- Limites semanais por instrumento
- Regras de reposição

# 3. Configurações financeiras
- Planos de mensalidade
- Descontos automáticos
- Integrações de pagamento

# 4. Notificações
- Templates de email
- Preferências de canal
- Horários silenciosos
```

## 🔍 Verificação da Instalação

### Testes Automáticos

```bash
# Executar testes
python -m pytest

# Verificar saúde do sistema
curl http://localhost:8000/health

# Testar banco de dados
python -c "from app import db; db.create_all(); print('DB OK')"

# Testar email
python -c "from app import mail; mail.send_email_test()"
```

### Checklist de Verificação

- [ ] ✅ Aplicação inicia sem erros
- [ ] ✅ Banco de dados conectado
- [ ] ✅ Redis funcionando
- [ ] ✅ Email configurado
- [ ] ✅ Admin pode fazer login
- [ ] ✅ Páginas carregam corretamente
- [ ] ✅ Formulários funcionam
- [ ] ✅ Relatórios gerados

## 🚀 Pós-Instalação

### Configurações de Produção

```bash
# Instalar SSL
sudo certbot --nginx -d seu-dominio.com

# Configurar backup automático
crontab -e
# Adicionar: 0 2 * * * /path/to/backup.sh

# Configurar monitoramento
# Instalar Prometheus/Grafana ou similar
```

### Próximos Passos

1. **Importar dados existentes** (se houver)
2. **Treinar equipe** usando os guias de usuário
3. **Configurar integrações** (gateways, email)
4. **Testar funcionalidades** com dados reais
5. **Planejar manutenção** regular

---

!!! success "Instalação Concluída!"

    Seu Sistema Sol Maior está pronto para uso. Acesse a documentação de [Primeiro Acesso](first-access.md) para começar.

!!! warning "Importante"

    - **Altere a senha padrão** do administrador imediatamente
    - **Configure backups** automáticos
    - **Monitore logs** regularmente
    - **Mantenha dependências** atualizadas

!!! tip "Suporte"

    Em caso de problemas, consulte a seção de [Solução de Problemas](../support/troubleshooting.md) ou entre em contato conosco.