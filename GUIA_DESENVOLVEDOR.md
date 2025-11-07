# 👨‍💻 GUIA DO DESENVOLVEDOR - SOLMAIOR
## Referência Rápida para Implementação

**Versão:** 2.0 | **Data:** Outubro 2025

---

## 🚀 Quick Start

### 1. Configuração Inicial
```bash
# Clone o repositório
git clone <repo-url>
cd Sol MaiorSystem-1

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicialize banco de dados
flask init_db

# Execute a aplicação
python app.py
```

### 2. Acessar o Sistema
- **URL:** http://localhost:5000
- **Admin:** admin@solmaior.com / admin123

**Nota:** Apenas o usuário admin é criado automaticamente. 
Para criar professores, alunos e secretárias, acesse o painel admin após login.

---

## 📋 Estrutura de Pastas

```
app/
├── __init__.py              # Inicialização Flask
├── models.py                # Modelos SQLAlchemy
├── routes/
│   ├── auth.py              # Autenticação
│   ├── admin.py             # Painel admin
│   ├── teacher.py           # Painel professor
│   ├── student.py           # Painel aluno
│   ├── secretary.py         # Painel secretaria
│   ├── public.py            # Portal público
│   ├── documents.py         # Documentos
│   ├── financial.py         # Financeiro
│   └── recitals.py          # Recitais
├── templates/
│   ├── base.html            # Template base
│   ├── auth/                # Templates autenticação
│   ├── admin/               # Templates admin
│   ├── teacher/             # Templates professor
│   ├── student/             # Templates aluno
│   ├── secretary/           # Templates secretaria
│   ├── public/              # Templates públicos
│   ├── financial/           # Templates financeiro
│   └── recitals/            # Templates recitais
├── static/
│   ├── css/                 # Estilos customizados
│   ├── js/                  # Scripts customizados
│   └── images/              # Imagens
└── utils/                   # Utilitários
```

---

## 🎨 Padrão de Cores

### Cor Primária
```
#008bcd (Azul Ciano)
RGB: 0, 139, 205
HSL: 195°, 100%, 40%
```

### Tailwind CSS Classes
```html
<!-- Fundo -->
<div class="bg-cyan-600">...</div>
<div class="bg-blue-600">...</div>

<!-- Texto -->
<p class="text-cyan-600">...</p>
<p class="text-blue-600">...</p>

<!-- Hover -->
<button class="hover:bg-cyan-700">...</button>

<!-- Gradiente -->
<div class="bg-gradient-to-r from-cyan-600 to-blue-600">...</div>

<!-- Semáforo -->
<span class="bg-green-500">OK</span>
<span class="bg-yellow-500">Atenção</span>
<span class="bg-red-500">Erro</span>
```

---

## 🔐 Modelos Principais

### User
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20))  # admin, teacher, student, secretary
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Teacher
```python
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instrument = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    hourly_rate = db.Column(db.Numeric(10, 2))  # Valor hora-aula
    bio = db.Column(db.Text)
    availabilities = db.relationship('TeacherAvailability', backref='teacher')
```

### Student
```python
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instrument = db.Column(db.String(50))
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    monthly_fee = db.Column(db.Numeric(10, 2))  # Mensalidade
    payment_type = db.Column(db.String(20))  # integral, installment
    installments = db.Column(db.Integer)  # Número de parcelas
    guardian_name = db.Column(db.String(120))
    guardian_phone = db.Column(db.String(20))
```

### LessonSchedule
```python
class LessonSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 30 ou 60 minutos
    status = db.Column(db.String(20))  # confirmada, pendente, cancelada, etc
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Billing
```python
class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    amount = db.Column(db.Numeric(10, 2))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20))  # pending, paid, overdue
    payment_method = db.Column(db.String(20))  # pix, card, boleto, etc
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🔧 Validações Comuns

### Validar Disponibilidade do Professor
```python
def validate_teacher_availability(teacher_id, start_time, end_time):
    """Verifica se professor está disponível no horário"""
    availability = TeacherAvailability.query.filter_by(
        teacher_id=teacher_id,
        day_of_week=start_time.weekday()
    ).first()
    
    if not availability:
        return False, "Professor não tem disponibilidade neste dia"
    
    if start_time.time() < availability.start_time or \
       end_time.time() > availability.end_time:
        return False, "Horário fora da disponibilidade"
    
    return True, "OK"
```

### Validar Conflito de Horário
```python
def check_schedule_conflict(teacher_id, student_id, room_id, start_time, end_time):
    """Verifica conflitos de professor, aluno e sala"""
    
    # Conflito de professor
    teacher_conflict = LessonSchedule.query.filter(
        LessonSchedule.teacher_id == teacher_id,
        LessonSchedule.start_time < end_time,
        LessonSchedule.end_time > start_time,
        LessonSchedule.status != 'cancelada'
    ).first()
    
    if teacher_conflict:
        return False, "Professor já tem aula neste horário"
    
    # Conflito de aluno
    student_conflict = LessonSchedule.query.filter(
        LessonSchedule.student_id == student_id,
        LessonSchedule.start_time < end_time,
        LessonSchedule.end_time > start_time,
        LessonSchedule.status != 'cancelada'
    ).first()
    
    if student_conflict:
        return False, "Aluno já tem aula neste horário"
    
    # Conflito de sala
    room_conflict = LessonSchedule.query.filter(
        LessonSchedule.room_id == room_id,
        LessonSchedule.start_time < end_time,
        LessonSchedule.end_time > start_time,
        LessonSchedule.status != 'cancelada'
    ).first()
    
    if room_conflict:
        return False, "Sala já está ocupada neste horário"
    
    return True, "OK"
```

### Validar Limite Semanal do Aluno
```python
def check_weekly_limit(student_id, duration, week_start):
    """Verifica se aluno não excede 60 minutos por semana"""
    week_end = week_start + timedelta(days=7)
    
    total_minutes = db.session.query(
        db.func.sum(LessonSchedule.duration)
    ).filter(
        LessonSchedule.student_id == student_id,
        LessonSchedule.start_time >= week_start,
        LessonSchedule.start_time < week_end,
        LessonSchedule.status != 'cancelada'
    ).scalar() or 0
    
    if total_minutes + duration > 60:
        return False, f"Aluno já tem {total_minutes} minutos. Limite: 60 minutos/semana"
    
    return True, "OK"
```

---

## 📧 Envio de Emails

### Configuração
```python
# Em config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'seu-email@gmail.com'
MAIL_PASSWORD = 'sua-senha-app'
```

### Enviar Email
```python
from flask_mail import Mail, Message

mail = Mail(app)

def send_email(subject, recipients, body, html=None):
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html
    )
    mail.send(msg)

# Uso
send_email(
    subject="Confirmação de Aula",
    recipients=[aluno.email],
    body="Sua aula foi agendada com sucesso",
    html="<h1>Confirmação de Aula</h1><p>Sua aula foi agendada!</p>"
)
```

---

## 🛡️ Proteção CSRF

### Em Templates HTML
```html
<form method="POST" action="/admin/schedule">
    {{ csrf_token() }}
    <input type="text" name="student_name">
    <button type="submit">Agendar</button>
</form>
```

### Em Rotas Flask
```python
from flask_wtf.csrf import csrf_protect

@app.route('/admin/schedule', methods=['POST'])
@csrf_protect
def schedule_lesson():
    # Código aqui
    pass
```

---

## 🔑 Controle de Acesso

### Decoradores de Proteção
```python
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Uso
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')
```

---

## 📊 Gerar Relatórios

### Relatório de Horas do Professor
```python
def generate_teacher_report(teacher_id, month, year):
    """Gera relatório de horas lecionadas"""
    lessons = LessonSchedule.query.filter(
        LessonSchedule.teacher_id == teacher_id,
        db.extract('month', LessonSchedule.start_time) == month,
        db.extract('year', LessonSchedule.start_time) == year,
        LessonSchedule.status.in_(['realizada', 'falta'])
    ).all()
    
    total_hours = sum(lesson.duration for lesson in lessons) / 60
    teacher = Teacher.query.get(teacher_id)
    amount = total_hours * float(teacher.hourly_rate)
    
    return {
        'teacher_name': teacher.user.full_name,
        'total_lessons': len(lessons),
        'total_hours': total_hours,
        'hourly_rate': float(teacher.hourly_rate),
        'amount': amount
    }
```

### Relatório de Alunos Inadimplentes
```python
def generate_overdue_report():
    """Gera relatório de alunos com atraso"""
    overdue = Billing.query.filter(
        Billing.status == 'overdue',
        Billing.due_date < datetime.now().date()
    ).all()
    
    report = []
    for billing in overdue:
        student = Student.query.get(billing.student_id)
        days_overdue = (datetime.now().date() - billing.due_date).days
        report.append({
            'student_name': student.user.full_name,
            'amount': float(billing.amount),
            'due_date': billing.due_date,
            'days_overdue': days_overdue
        })
    
    return report
```

---

## 🧪 Testes

### Estrutura de Teste
```python
import unittest
from app import create_app, db

class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_schedule_lesson(self):
        """Testa agendamento de aula"""
        response = self.client.post('/admin/schedule', data={
            'student_id': 1,
            'teacher_id': 1,
            'room_id': 1,
            'start_time': '2025-11-01 14:00',
            'duration': 60
        })
        self.assertEqual(response.status_code, 200)
```

### Executar Testes
```bash
python -m pytest tests/
# ou
python -m unittest discover tests/
```

---

## 🐛 Debug

### Ativar Debug Mode
```python
# Em app.py
if __name__ == '__main__':
    app.run(debug=True)
```

### Logs
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Mensagem de debug")
logger.info("Mensagem de info")
logger.warning("Mensagem de aviso")
logger.error("Mensagem de erro")
```

### Debugger do Flask
```python
from flask import current_app

@app.route('/debug')
def debug():
    current_app.logger.debug('Mensagem de debug')
    return "Check console"
```

---

## 📦 Dependências

### Instalar Nova Dependência
```bash
pip install nome-do-pacote
pip freeze > requirements.txt
```

### Atualizar Dependências
```bash
pip install --upgrade -r requirements.txt
```

---

## 🚀 Deploy

### Preparar para Produção
```bash
# Desativar debug
DEBUG = False

# Usar HTTPS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Configurar SECRET_KEY segura
SECRET_KEY = os.environ.get('SECRET_KEY')
```

### Deploy no Heroku
```bash
heroku create solmaior
git push heroku main
heroku run flask db upgrade
```

---

## 📝 Convenções de Código

### Nomenclatura
- **Variáveis:** snake_case
- **Classes:** PascalCase
- **Constantes:** UPPER_CASE
- **Funções:** snake_case

### Exemplo
```python
class StudentSchedule:
    MAX_WEEKLY_MINUTES = 60
    
    def __init__(self, student_id):
        self.student_id = student_id
        self.lessons = []
    
    def add_lesson(self, lesson):
        self.lessons.append(lesson)
    
    def get_total_minutes(self):
        return sum(lesson.duration for lesson in self.lessons)
```

---

## 🔗 Links Úteis

- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Tailwind CSS:** https://tailwindcss.com/
- **Alpine.js:** https://alpinejs.dev/
- **PostgreSQL:** https://www.postgresql.org/docs/

---

## 📞 Suporte

**Dúvidas ou problemas?**
- Verifique a documentação em ARQUITETURA_SISTEMA.md
- Consulte REGRAS_NEGOCIO.md para regras específicas
- Abra uma issue no repositório

---

**Última atualização:** Outubro 2025
**Versão:** 2.0
