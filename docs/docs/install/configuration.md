# ⚙️ Configuração do Sistema

!!! info "Configurações Essenciais"

    Aprenda a configurar corretamente todas as funcionalidades do Sistema Sol Maior.

## 🔧 Arquivo de Configuração

### Estrutura Básica

```python
# config.py
import os
from datetime import timedelta

class Config:
    """Configuração base"""

    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-segura-32-caracteres'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-key-segura'

    # Flask
    DEBUG = False
    TESTING = False
    SESSION_TYPE = 'redis'

    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Sessões
    SESSION_REDIS = REDIS_URL
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Paginação
    ITEMS_PER_PAGE = 20

    # Logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False

    # Configurações de produção obrigatórias
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.environ.get('DATABASE_URL')

# Selecionar configuração baseada na variável de ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

current_config = config.get(os.environ.get('FLASK_ENV') or 'default', DevelopmentConfig)
```

## 🏫 Configurações da Instituição

### Informações Básicas

```python
# No painel admin > Configurações > Instituição

INSTITUTION_CONFIG = {
    'name': 'Escola de Música Sol Maior',
    'short_name': 'Sol Maior',
    'cnpj': '00.000.000/0001-00',
    'address': {
        'street': 'Rua das Artes, 123',
        'city': 'São Paulo',
        'state': 'SP',
        'zip_code': '01234-567',
        'country': 'Brasil'
    },
    'contact': {
        'phone': '(11) 99999-9999',
        'email': 'contato@solmaior.com.br',
        'website': 'https://solmaior.com.br'
    },
    'social_media': {
        'facebook': 'https://facebook.com/solmaior',
        'instagram': '@solmaior.musica',
        'youtube': 'https://youtube.com/solmaior'
    }
}
```

### Políticas Acadêmicas

```python
# Configurações de aulas e horários

ACADEMIC_POLICIES = {
    'lesson_duration': {
        'default': 60,  # minutos
        'min': 30,
        'max': 120
    },
    'weekly_limits': {
        'piano': {'min': 30, 'max': 60},
        'violino': {'min': 45, 'max': 90},
        'canto': {'min': 30, 'max': 60},
        'teoria': {'min': 45, 'max': 90}
    },
    'makeup_policy': {
        'max_advance_days': 30,
        'expiration_days': 7,
        'auto_create': True
    },
    'attendance_policy': {
        'grace_period_minutes': 15,
        'auto_absence_hours': 24
    }
}
```

## 💰 Configurações Financeiras

### Planos de Mensalidade

```python
# Planos disponíveis

BILLING_PLANS = {
    'individual': {
        'name': 'Aula Individual',
        'monthly_value': 150.00,
        'lessons_per_month': 4,
        'description': 'Aulas individuais semanais'
    },
    'duo': {
        'name': 'Aula em Duo',
        'monthly_value': 100.00,
        'lessons_per_month': 4,
        'description': 'Aulas compartilhadas (2 alunos)'
    },
    'group': {
        'name': 'Aula em Grupo',
        'monthly_value': 80.00,
        'lessons_per_month': 4,
        'description': 'Aulas coletivas (3-5 alunos)'
    }
}
```

### Descontos Automáticos

```python
# Sistema de descontos

DISCOUNT_POLICIES = {
    'frequency_discount': {
        'enabled': True,
        'rules': [
            {'attendance_rate': 100, 'discount_percent': 10},
            {'attendance_rate': 95, 'discount_percent': 5},
            {'attendance_rate': 90, 'discount_percent': 3},
            {'attendance_rate': 80, 'discount_percent': 2}
        ]
    },
    'sibling_discount': {
        'enabled': True,
        'discount_percent': 15,
        'max_siblings': 3
    },
    'early_payment_discount': {
        'enabled': True,
        'discount_percent': 5,
        'days_before_due': 10
    }
}
```

### Gateways de Pagamento

```python
# Configuração dos gateways

PAYMENT_GATEWAYS = {
    'mercado_pago': {
        'enabled': True,
        'access_token': os.environ.get('MERCADO_PAGO_ACCESS_TOKEN'),
        'public_key': os.environ.get('MERCADO_PAGO_PUBLIC_KEY'),
        'sandbox': os.environ.get('FLASK_ENV') != 'production',
        'webhook_url': f"{os.environ.get('BASE_URL')}/webhooks/mercadopago"
    },
    'pagseguro': {
        'enabled': False,
        'email': os.environ.get('PAGSEGURO_EMAIL'),
        'token': os.environ.get('PAGSEGURO_TOKEN'),
        'sandbox': os.environ.get('FLASK_ENV') != 'production'
    },
    'stripe': {
        'enabled': False,
        'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
        'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY'),
        'webhook_secret': os.environ.get('STRIPE_WEBHOOK_SECRET')
    }
}
```

## 📧 Configurações de Comunicação

### Templates de Email

```python
# Templates de notificação

EMAIL_TEMPLATES = {
    'lesson_reminder': {
        'subject': 'Lembrete: Você tem aula amanhã!',
        'template': 'lesson_reminder.html',
        'priority': 'high'
    },
    'payment_due': {
        'subject': 'Aviso: Mensalidade vence em breve',
        'template': 'payment_due.html',
        'priority': 'high'
    },
    'makeup_available': {
        'subject': 'Sugestões de reposição disponíveis',
        'template': 'makeup_available.html',
        'priority': 'medium'
    }
}
```

### Preferências de Notificação

```python
# Configurações padrão de notificação

DEFAULT_NOTIFICATION_PREFERENCES = {
    'lesson_reminder': {
        'email': True,
        'sms': False,
        'push': True,
        'frequency': 'immediate',
        'quiet_hours_start': '22:00',
        'quiet_hours_end': '08:00'
    },
    'payment_due': {
        'email': True,
        'sms': True,
        'push': True,
        'frequency': 'immediate'
    },
    'news': {
        'email': True,
        'sms': False,
        'push': False,
        'frequency': 'weekly'
    }
}
```

## 🔐 Configurações de Segurança

### Autenticação

```python
# Configurações de login e sessão

AUTH_CONFIG = {
    'session_timeout': timedelta(hours=8),
    'password_min_length': 8,
    'password_require_uppercase': True,
    'password_require_numbers': True,
    'password_require_special': True,
    'max_login_attempts': 5,
    'lockout_duration': timedelta(minutes=30),
    'jwt_secret_key': os.environ.get('JWT_SECRET_KEY'),
    'jwt_access_token_expire': timedelta(hours=1),
    'jwt_refresh_token_expire': timedelta(days=30)
}
```

### Backup e Recuperação

```python
# Configurações de backup

BACKUP_CONFIG = {
    'enabled': True,
    'frequency': 'daily',  # daily, weekly, monthly
    'time': '02:00',  # HH:MM
    'retention_days': 30,
    'storage_path': '/var/backups/solmaior',
    'compress': True,
    'encrypt': True,
    'encryption_key': os.environ.get('BACKUP_ENCRYPTION_KEY'),
    'remote_storage': {
        'enabled': False,
        'provider': 'aws_s3',  # aws_s3, gcp_storage, azure_blob
        'bucket': 'solmaior-backups',
        'region': 'us-east-1'
    }
}
```

## 📊 Configurações de Analytics

### Indicadores Preditivos

```python
# Configurações de machine learning

PREDICTIVE_CONFIG = {
    'churn_prediction': {
        'enabled': True,
        'risk_threshold': 50,  # 0-100
        'lookback_days': 90,
        'update_frequency': 'daily'
    },
    'revenue_forecast': {
        'enabled': True,
        'forecast_days': 30,
        'confidence_interval': 0.95
    },
    'demand_forecast': {
        'enabled': True,
        'instruments_to_track': ['piano', 'violino', 'canto'],
        'seasonal_adjustment': True
    }
}
```

### Relatórios Automáticos

```python
# Configurações de relatórios

REPORT_CONFIG = {
    'auto_generate': {
        'monthly_financial': True,
        'weekly_attendance': True,
        'student_progress': True
    },
    'recipients': {
        'admin_emails': ['admin@solmaior.com'],
        'secretary_emails': ['secretaria@solmaior.com']
    },
    'schedule': {
        'monthly_financial': {'day': 1, 'time': '09:00'},
        'weekly_attendance': {'weekday': 1, 'time': '08:00'},  # Monday
        'student_progress': {'day': 15, 'time': '10:00'}
    }
}
```

## 🎭 Configurações de Recitais

### Políticas de Evento

```python
# Configurações de recitais

RECITAL_CONFIG = {
    'default_duration': 120,  # minutos
    'max_participants': 50,
    'registration_deadline_days': 7,
    'certificate_generation': 'automatic',  # automatic, manual, disabled
    'ticket_system': {
        'enabled': False,
        'price': 0.00,
        'max_tickets_per_person': 4
    },
    'recording': {
        'enabled': True,
        'auto_upload': True,
        'storage_provider': 'youtube'  # youtube, vimeo, local
    }
}
```

## 🔧 Configurações Técnicas

### Performance

```python
# Otimizações de performance

PERFORMANCE_CONFIG = {
    'cache': {
        'enabled': True,
        'ttl': 3600,  # 1 hour
        'redis_url': os.environ.get('REDIS_URL')
    },
    'database': {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600
    },
    'file_upload': {
        'max_size': 10 * 1024 * 1024,  # 10MB
        'allowed_extensions': ['pdf', 'jpg', 'jpeg', 'png', 'mp3', 'wav']
    }
}
```

### Monitoramento

```python
# Configurações de monitoramento

MONITORING_CONFIG = {
    'enabled': True,
    'metrics': {
        'response_time': True,
        'error_rate': True,
        'database_connections': True,
        'memory_usage': True,
        'cpu_usage': True
    },
    'alerts': {
        'email_recipients': ['admin@solmaior.com'],
        'error_threshold': 5,  # errors per minute
        'response_time_threshold': 2000  # milliseconds
    },
    'external_services': {
        'sentry_dsn': os.environ.get('SENTRY_DSN'),
        'prometheus_url': os.environ.get('PROMETHEUS_URL')
    }
}
```

## 🚀 Implantação

### Variáveis de Ambiente

```bash
# Arquivo .env para produção
SECRET_KEY=your-32-char-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port/db
MAIL_SERVER=smtp.sendgrid.net
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
FLASK_ENV=production
BASE_URL=https://your-domain.com
```

### Verificação de Configuração

```python
# Script de verificação
def verify_configuration():
    """Verifica se todas as configurações necessárias estão presentes"""

    required_configs = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]

    missing = []
    for config in required_configs:
        if not os.environ.get(config):
            missing.append(config)

    if missing:
        raise ValueError(f"Configurações obrigatórias faltando: {', '.join(missing)}")

    print("✅ Todas as configurações verificadas com sucesso!")

if __name__ == '__main__':
    verify_configuration()
```

---

!!! success "Sistema Configurado!"

    Com essas configurações, seu Sistema Sol Maior estará totalmente personalizado para sua instituição.

!!! tip "Próximo Passo"

    Após configurar, siga para o [Primeiro Acesso](first-access.md) para começar a usar o sistema.