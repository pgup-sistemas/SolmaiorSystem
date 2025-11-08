# 📋 Pré-requisitos

!!! info "Antes de Instalar"

    Verifique se seu ambiente atende aos requisitos mínimos para executar o Sistema Sol Maior.

## 💻 Requisitos de Hardware

### Servidor de Produção
| Componente | Mínimo | Recomendado | Para Grandes Redes |
|------------|--------|-------------|-------------------|
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **RAM** | 4 GB | 8 GB | 16 GB+ |
| **Armazenamento** | 50 GB SSD | 100 GB SSD | 500 GB+ SSD |
| **Rede** | 10 Mbps | 100 Mbps | 1 Gbps |

### Ambiente de Desenvolvimento
| Componente | Especificação |
|------------|---------------|
| **CPU** | 2+ cores modernos |
| **RAM** | 4 GB+ |
| **Armazenamento** | 20 GB disponível |
| **SO** | Linux/macOS/Windows |

## 🖥️ Sistemas Operacionais Suportados

### ✅ Linux (Recomendado)
- **Ubuntu** 20.04 LTS ou superior
- **CentOS/RHEL** 8.0 ou superior
- **Debian** 11 ou superior
- **Amazon Linux** 2 ou superior

### ✅ macOS
- **macOS Monterey** (12.0) ou superior
- **Intel ou Apple Silicon** (M1/M2)

### ⚠️ Windows
- **Windows 10/11** Pro ou superior
- **WSL2** recomendado para desenvolvimento
- **Windows Server** 2019+ para produção

## 🐍 Python e Dependências

### Versão do Python
```bash
# Verificar versão instalada
python3 --version
# Deve ser 3.8 ou superior

# Ou usando pyenv
pyenv versions
```

### Gerenciador de Pacotes
```bash
# Instalar pip (geralmente já vem com Python)
python3 -m ensurepip --upgrade

# Verificar versão
pip --version
```

### Ambiente Virtual
```bash
# Instalar virtualenv
pip install virtualenv

# Criar ambiente virtual
virtualenv venv

# Ativar ambiente
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

## 🗄️ Banco de Dados

### PostgreSQL (Recomendado)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verificar instalação
psql --version

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### MySQL/MariaDB (Alternativo)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Configurar segurança
sudo mysql_secure_installation

# Verificar instalação
mysql --version
```

### Redis (Cache e Sessões)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Iniciar serviço
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar funcionamento
redis-cli ping  # Deve retornar PONG
```

## 🌐 Servidor Web

### Nginx (Recomendado)
```bash
# Instalar
sudo apt update
sudo apt install nginx

# Iniciar serviço
sudo systemctl start nginx
sudo systemctl enable nginx

# Verificar status
sudo systemctl status nginx
```

### Apache (Alternativo)
```bash
# Instalar
sudo apt update
sudo apt install apache2

# Iniciar serviço
sudo systemctl start apache2
sudo systemctl enable apache2
```

## 🔧 Ferramentas de Desenvolvimento

### Git
```bash
# Instalar
sudo apt update
sudo apt install git

# Configurar
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Verificar
git --version
```

### Node.js e NPM (para assets)
```bash
# Instalar Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar
node --version
npm --version
```

### Docker (Opcional, para desenvolvimento)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version
```

## 📧 Serviços de Email

### Configuração SMTP
O sistema suporta diversos provedores:

- **SendGrid** (Recomendado)
- **Amazon SES**
- **Gmail SMTP**
- **Mailgun**
- **Servidor próprio**

### Exemplo de configuração
```python
# config.py
MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'apikey'
MAIL_PASSWORD = 'your-sendgrid-api-key'
```

## 🔑 Chaves e Credenciais

### Gateways de Pagamento
Prepare as credenciais para os gateways que deseja usar:

#### Mercado Pago
- `MERCADO_PAGO_ACCESS_TOKEN`
- `MERCADO_PAGO_PUBLIC_KEY`

#### PagSeguro
- `PAGSEGURO_EMAIL`
- `PAGSEGURO_TOKEN`

#### Stripe
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`

### Outras APIs
- **Redis URL**: `redis://localhost:6379/0`
- **Database URL**: `postgresql://user:password@localhost/solmaior`
- **Secret Key**: Gerar chave segura de 32 caracteres

## 🔒 Segurança

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Verificar status
sudo ufw status
```

### SSL Certificate
```bash
# Instalar Certbot para Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d seusite.com
```

### Backup
```bash
# Instalar ferramentas de backup
sudo apt install rsync
sudo apt install duplicity

# Criar diretório de backup
sudo mkdir -p /backup
sudo chown $USER:$USER /backup
```

## 📊 Monitoramento

### Ferramentas Básicas
```bash
# Instalar htop para monitoramento
sudo apt install htop

# Instalar ferramentas de rede
sudo apt install net-tools curl wget

# Verificar conectividade
curl -I https://google.com
```

## ✅ Checklist de Verificação

Antes de prosseguir com a instalação, execute:

```bash
# 1. Verificar Python
python3 --version  # 3.8+

# 2. Verificar pip
pip --version

# 3. Verificar Git
git --version

# 4. Verificar PostgreSQL
sudo systemctl status postgresql

# 5. Verificar Redis
redis-cli ping

# 6. Verificar Nginx
sudo systemctl status nginx

# 7. Verificar espaço em disco
df -h

# 8. Verificar memória
free -h
```

!!! success "Ambiente Pronto!"

    Se todos os checks passaram, seu ambiente está pronto para a instalação do Sistema Sol Maior.

!!! warning "Problemas Comuns"

    - **Python versão antiga**: Use `pyenv` para instalar versão mais recente
    - **PostgreSQL não inicia**: Verificar logs em `/var/log/postgresql/`
    - **Redis falha**: Verificar configuração em `/etc/redis/redis.conf`
    - **Permissões**: Usar `sudo` quando necessário, mas evitar para desenvolvimento

!!! tip "Próximo Passo"

    Com o ambiente preparado, siga para a [Instalação](installation.md) do sistema.