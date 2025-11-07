
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    avatar_url = db.Column(db.String(500))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

    __table_args__ = (
        db.Index('idx_user_role_active', 'role', 'is_active'),
    )


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    instrument = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200))
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    availabilities = db.relationship('TeacherAvailability', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')
    lessons = db.relationship('LessonSchedule', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')
    recital_participations = db.relationship('RecitalParticipant', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', foreign_keys='Document.related_teacher_id', backref='related_teacher', lazy='dynamic')

    def __repr__(self):
        return f'<Teacher {self.user.full_name} - {self.instrument}>'


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    instrument = db.Column(db.String(100), nullable=False, index=True)
    level = db.Column(db.String(50), index=True)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)

    # Dados do Responsável (obrigatório para menores)
    guardian_name = db.Column(db.String(200))
    guardian_phone = db.Column(db.String(20))
    guardian_email = db.Column(db.String(120))
    guardian_cpf = db.Column(db.String(14))

    # Dados Pessoais
    birth_date = db.Column(db.Date)
    cpf = db.Column(db.String(14), unique=True, index=True)
    rg = db.Column(db.String(20))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(10))

    # Informações do Curso
    course_modality = db.Column(db.String(50))  # Individual, Grupo, Online
    weekly_lessons = db.Column(db.Integer, default=1)
    lesson_duration = db.Column(db.Integer, default=60)  # minutos
    preferred_schedule = db.Column(db.String(100))

    # Outras informações
    medical_info = db.Column(db.Text)
    special_needs = db.Column(db.Text)
    previous_experience = db.Column(db.Text)
    goals = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    lessons = db.relationship('LessonSchedule', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    recital_participations = db.relationship('RecitalParticipant', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', foreign_keys='Document.related_student_id', backref='related_student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.user.full_name} - {self.instrument}>'

    __table_args__ = (
        db.Index('idx_student_instrument_level', 'instrument', 'level'),
        db.Index('idx_student_active', 'is_active'),
    )


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    capacity = db.Column(db.Integer, default=1, nullable=False)
    equipment = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    schedules = db.relationship('LessonSchedule', backref='room', lazy='dynamic')

    def __repr__(self):
        return f'<Room {self.name}>'


class TeacherAvailability(db.Model):
    __tablename__ = 'teacher_availability'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Segunda, 6=Domingo
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_recurring = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return f'<Availability {self.teacher.user.full_name} - {days[self.day_of_week]} {self.start_time}-{self.end_time}>'

    __table_args__ = (
        db.Index('idx_teacher_day', 'teacher_id', 'day_of_week'),
        db.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='check_day_of_week'),
        db.CheckConstraint('start_time < end_time', name='check_time_range'),
    )


class LessonSchedule(db.Model):
    __tablename__ = 'lesson_schedule'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='SET NULL'))
    lesson_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled', index=True)  # scheduled, completed, cancelled, absent
    lesson_type = db.Column(db.String(20), default='regular')  # regular, makeup, trial
    notes = db.Column(db.Text)
    
    # Novas funcionalidades Professor
    attendance_confirmed = db.Column(db.Boolean, default=False)
    attendance_status = db.Column(db.String(20))  # present, absent, late, justified
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    confirmed_at = db.Column(db.DateTime)
    lesson_notes = db.Column(db.Text)  # Notas do professor sobre a aula
    lesson_content = db.Column(db.Text)  # Conteúdo ministrado
    homework_assigned = db.Column(db.Text)  # Lição de casa
    student_progress = db.Column(db.String(20))  # excellent, good, satisfactory, needs_improvement
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    confirmer = db.relationship('User', foreign_keys=[confirmed_by])

    def __repr__(self):
        return f'<Lesson {self.student.user.full_name} - {self.lesson_date} {self.start_time}>'

    __table_args__ = (
        db.Index('idx_lesson_date', 'lesson_date'),
        db.Index('idx_teacher_date', 'teacher_id', 'lesson_date'),
        db.Index('idx_student_date', 'student_id', 'lesson_date'),
        db.Index('idx_room_date', 'room_id', 'lesson_date'),
        db.Index('idx_lesson_status', 'status'),
        db.CheckConstraint('start_time < end_time', name='check_lesson_time_range'),
    )


class MakeupLesson(db.Model):
    __tablename__ = 'makeup_lessons'

    id = db.Column(db.Integer, primary_key=True)
    original_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id', ondelete='CASCADE'), nullable=False)
    new_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id', ondelete='SET NULL'))
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, rejected, scheduled
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    original_lesson = db.relationship('LessonSchedule', foreign_keys=[original_lesson_id], backref='makeup_requests')
    new_lesson = db.relationship('LessonSchedule', foreign_keys=[new_lesson_id])
    requester = db.relationship('User', foreign_keys=[requested_by], backref='makeup_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_makeups')

    def __repr__(self):
        return f'<MakeupLesson {self.id} - {self.status}>'

    __table_args__ = (
        db.Index('idx_makeup_status', 'status'),
    )


class Recital(db.Model):
    __tablename__ = 'recitals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False, index=True)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='planned', index=True)  # planned, confirmed, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = db.relationship('User', backref=db.backref('created_recitals', lazy='dynamic'))
    performances = db.relationship('RecitalPerformance', backref='recital', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Recital {self.title} - {self.event_date}>'

    __table_args__ = (
        db.Index('idx_recital_date_status', 'event_date', 'status'),
    )


class RecitalPerformance(db.Model):
    __tablename__ = 'recital_performances'

    id = db.Column(db.Integer, primary_key=True)
    recital_id = db.Column(db.Integer, db.ForeignKey('recitals.id', ondelete='CASCADE'), nullable=False)
    performance_type = db.Column(db.String(50), nullable=False)  # solo, duo, group, choir, band
    piece_title = db.Column(db.String(200), nullable=False)
    composer = db.Column(db.String(200))
    duration_minutes = db.Column(db.Integer)
    order_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    participants = db.relationship('RecitalParticipant', backref='performance', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Performance {self.piece_title} ({self.performance_type})>'

    __table_args__ = (
        db.Index('idx_performance_recital', 'recital_id', 'order_number'),
    )


class RecitalParticipant(db.Model):
    __tablename__ = 'recital_participants'

    id = db.Column(db.Integer, primary_key=True)
    performance_id = db.Column(db.Integer, db.ForeignKey('recital_performances.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'))
    role = db.Column(db.String(50))  # performer, accompanist, conductor
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        if self.student_id:
            return f'<Participant Student:{self.student.user.full_name}>'
        return f'<Participant Teacher:{self.teacher.user.full_name}>'

    __table_args__ = (
        db.CheckConstraint(
            '(student_id IS NOT NULL AND teacher_id IS NULL) OR (student_id IS NULL AND teacher_id IS NOT NULL)',
            name='check_participant_type'
        ),
    )


class NewsPost(db.Model):
    __tablename__ = 'news_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type = db.Column(db.String(20), default='news', index=True)  # news, event, announcement
    is_published = db.Column(db.Boolean, default=False, index=True)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = db.relationship('User', backref=db.backref('news_posts', lazy='dynamic'))

    def __repr__(self):
        return f'<NewsPost {self.title}>'

    __table_args__ = (
        db.Index('idx_news_published', 'is_published', 'published_at'),
    )


class TrialLesson(db.Model):
    __tablename__ = 'trial_lessons'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    instrument = db.Column(db.String(100), nullable=False)
    preferred_date = db.Column(db.Date)
    preferred_time = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, scheduled, completed, cancelled
    
    # Campos de agendamento
    scheduled_date = db.Column(db.Date)  # Data confirmada do agendamento
    scheduled_time = db.Column(db.Time)  # Hora confirmada do agendamento
    assigned_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    duration_minutes = db.Column(db.Integer, default=60)  # Duração da aula em minutos
    confirmation_sent = db.Column(db.Boolean, default=False)  # Email de confirmação enviado
    notes = db.Column(db.Text)  # Observações internas
    
    # Campos de confirmação do usuário
    confirmation_token = db.Column(db.String(100), unique=True)  # Token único para confirmação
    user_confirmed = db.Column(db.Boolean, default=False)  # Se usuário confirmou presença
    user_confirmed_at = db.Column(db.DateTime)  # Quando confirmou
    user_declined = db.Column(db.Boolean, default=False)  # Se usuário recusou
    user_declined_at = db.Column(db.DateTime)  # Quando recusou
    reminder_sent = db.Column(db.Boolean, default=False)  # Lembrete enviado
    reminder_sent_at = db.Column(db.DateTime)  # Quando lembrete foi enviado
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    assigned_teacher = db.relationship('Teacher', backref='trial_lessons')
    room = db.relationship('Room', backref='trial_lessons')

    def __repr__(self):
        return f'<TrialLesson {self.full_name} - {self.instrument}>'

    __table_args__ = (
        db.Index('idx_trial_status', 'status'),
        db.Index('idx_trial_scheduled_date', 'scheduled_date'),
    )


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # mensal, trimestral, semestral, anual
    monthly_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, suspended, cancelled, completed
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payments = db.relationship('Payment', backref='enrollment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Enrollment {self.student.user.full_name} - {self.plan_type}>'

    __table_args__ = (
        db.Index('idx_enrollment_status', 'status'),
        db.Index('idx_enrollment_dates', 'start_date', 'end_date'),
        db.CheckConstraint('monthly_value > 0', name='check_positive_value'),
    )


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False)
    reference_month = db.Column(db.Date, nullable=False, index=True)
    due_date = db.Column(db.Date, nullable=False, index=True)
    payment_date = db.Column(db.Date, index=True)
    amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    discount_reason = db.Column(db.String(255))  # Novo: razão do desconto
    late_fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, credit_card, debit_card, pix, bank_transfer
    status = db.Column(db.String(20), default='pending', index=True)  # pending, paid, cancelled, refunded
    receipt_number = db.Column(db.String(50), unique=True, index=True)
    
    # Novos campos para parcelamento
    is_installment = db.Column(db.Boolean, default=False)
    installment_number = db.Column(db.Integer)  # 1 de 3, 2 de 3, etc
    installment_total = db.Column(db.Integer)  # Total de parcelas
    parent_payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))  # Para rastrear parcelamentos
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento para parcelamento
    installments = db.relationship('Payment', backref=db.backref('parent_payment', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Payment {self.receipt_number or self.id} - {self.status}>'

    __table_args__ = (
        db.Index('idx_payment_status', 'status'),
        db.Index('idx_payment_due_date', 'due_date'),
        db.Index('idx_payment_enrollment_month', 'enrollment_id', 'reference_month'),
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
        db.CheckConstraint('discount >= 0', name='check_non_negative_discount'),
        db.CheckConstraint('late_fee >= 0', name='check_non_negative_late_fee'),
    )


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    category = db.Column(db.String(50), nullable=False, index=True)  # contract, score, audio, video, certificate, other
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
    related_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'))
    is_public = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy='dynamic'))

    def __repr__(self):
        return f'<Document {self.title} ({self.category})>'

    __table_args__ = (
        db.Index('idx_document_category', 'category'),
        db.Index('idx_document_public', 'is_public'),
    )


# ============================================================================
# NOVAS ENTIDADES - MELHORIAS v2.1
# ============================================================================

class LessonWaitlist(db.Model):
    """Fila de espera para aulas - Melhoria 1"""
    __tablename__ = 'lesson_waitlist'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False, index=True)
    instrument = db.Column(db.String(100), nullable=False)
    preferred_day = db.Column(db.String(20))  # Segunda, Terça, etc
    preferred_time = db.Column(db.String(10))  # 14:00, 15:00, etc
    duration = db.Column(db.Integer, default=60)  # 30 ou 60 minutos
    priority = db.Column(db.Integer, default=0)  # Ordem de chegada
    status = db.Column(db.String(20), default='waiting', index=True)  # waiting, matched, expired, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    matched_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # 30 dias
    notes = db.Column(db.Text)

    student = db.relationship('Student', backref=db.backref('waitlist_entries', lazy='dynamic'))
    teacher = db.relationship('Teacher', backref=db.backref('waitlist_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<LessonWaitlist {self.student.user.full_name} - {self.status}>'


class MakeupLessonSuggestion(db.Model):
    """Sugestões automáticas de reposição - Melhoria 2"""
    __tablename__ = 'makeup_lesson_suggestion'

    id = db.Column(db.Integer, primary_key=True)
    original_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    suggested_slots = db.Column(db.JSON)  # Array de 3 opções de horário
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, rejected
    accepted_slot = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)  # 7 dias
    notes = db.Column(db.Text)

    original_lesson = db.relationship('LessonSchedule', foreign_keys=[original_lesson_id])
    student = db.relationship('Student', backref=db.backref('makeup_suggestions', lazy='dynamic'))
    teacher = db.relationship('Teacher', backref=db.backref('makeup_suggestions', lazy='dynamic'))

    def __repr__(self):
        return f'<MakeupLessonSuggestion {self.student.user.full_name} - {self.status}>'


class InstrumentLessonPolicy(db.Model):
    """Política de limite dinâmico por instrumento - Melhoria 3"""
    __tablename__ = 'instrument_lesson_policy'

    id = db.Column(db.Integer, primary_key=True)
    instrument = db.Column(db.String(100), unique=True, nullable=False, index=True)
    min_weekly_minutes = db.Column(db.Integer, default=30)
    max_weekly_minutes = db.Column(db.Integer, default=60)
    recommended_duration = db.Column(db.Integer, default=60)  # 30 ou 60
    min_lessons_per_week = db.Column(db.Integer, default=1)
    max_lessons_per_week = db.Column(db.Integer, default=2)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<InstrumentLessonPolicy {self.instrument}>'


class StudentLessonCredit(db.Model):
    """Sistema de créditos de aula - Melhoria 4"""
    __tablename__ = 'student_lesson_credit'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    total_credits = db.Column(db.Integer, nullable=False)  # Número de aulas
    used_credits = db.Column(db.Integer, default=0)
    remaining_credits = db.Column(db.Integer)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active', index=True)  # active, expired, transferred
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    student = db.relationship('Student', backref=db.backref('lesson_credits', lazy='dynamic'))

    def __repr__(self):
        return f'<StudentLessonCredit {self.student.user.full_name} - {self.remaining_credits}/{self.total_credits}>'


class FrequencyDiscount(db.Model):
    """Desconto por frequência - Melhoria 5"""
    __tablename__ = 'frequency_discount'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    attendance_rate = db.Column(db.Float)  # 0-100%
    discount_percentage = db.Column(db.Float)
    reason = db.Column(db.String(100))  # "Frequência 100%"
    applied = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', backref=db.backref('frequency_discounts', lazy='dynamic'))

    def __repr__(self):
        return f'<FrequencyDiscount {self.student.user.full_name} - {self.discount_percentage}%>'

    __table_args__ = (
        db.Index('idx_frequency_discount_student_period', 'student_id', 'month', 'year'),
    )


class FinancialAuditLog(db.Model):
    """Auditoria financeira completa - Melhoria 6"""
    __tablename__ = 'financial_audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, approve
    entity_type = db.Column(db.String(50), nullable=False)  # Billing, Discount, Installment
    entity_id = db.Column(db.Integer)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = db.Column(db.String(20), default='success')  # success, failed

    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<FinancialAuditLog {self.action} - {self.entity_type}>'

    __table_args__ = (
        db.Index('idx_audit_log_entity', 'entity_type', 'entity_id'),
        db.Index('idx_audit_log_timestamp', 'timestamp'),
    )


class NotificationPreference(db.Model):
    """Preferências de notificação - Melhoria 7"""
    __tablename__ = 'notification_preference'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    notification_type = db.Column(db.String(50), nullable=False)  # lesson_reminder, payment_due, etc
    channel = db.Column(db.String(20), default='email')  # email, sms, push
    enabled = db.Column(db.Boolean, default=True)
    frequency = db.Column(db.String(20), default='immediate')  # immediate, daily, weekly
    quiet_hours_start = db.Column(db.Time)
    quiet_hours_end = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('notification_preferences', lazy='dynamic'))

    def __repr__(self):
        return f'<NotificationPreference {self.user.email} - {self.notification_type}>'

    __table_args__ = (
        db.Index('idx_notification_pref_user_type', 'user_id', 'notification_type'),
    )


class PredictiveIndicator(db.Model):
    """Indicadores preditivos para dashboard - Melhoria 8"""
    __tablename__ = 'predictive_indicator'

    id = db.Column(db.Integer, primary_key=True)
    indicator_type = db.Column(db.String(50), nullable=False, index=True)  # churn_risk, revenue_forecast, occupancy_forecast, demand_unmet
    entity_type = db.Column(db.String(50))  # Student, Teacher, Room
    entity_id = db.Column(db.Integer)
    value = db.Column(db.Float)  # Valor do indicador (0-100 para percentuais)
    description = db.Column(db.Text)
    action_required = db.Column(db.Boolean, default=False)
    action_description = db.Column(db.String(255))
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    valid_until = db.Column(db.DateTime)

    def __repr__(self):
        return f'<PredictiveIndicator {self.indicator_type} - {self.value}>'

    __table_args__ = (
        db.Index('idx_predictive_indicator_type', 'indicator_type'),
        db.Index('idx_predictive_indicator_entity', 'entity_type', 'entity_id'),
    )


class ScheduledNotification(db.Model):
    """Notificações agendadas - Automações"""
    __tablename__ = 'scheduled_notifications'

    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(50), nullable=False, index=True)  # lesson_reminder, payment_due, makeup_approved, etc
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_email = db.Column(db.String(120))
    recipient_phone = db.Column(db.String(20))
    
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    
    # Referências
    related_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id'))
    related_payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    related_makeup_id = db.Column(db.Integer, db.ForeignKey('makeup_lessons.id'))
    
    # Controle de envio
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, sent, failed, cancelled
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    recipient = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    related_lesson = db.relationship('LessonSchedule', foreign_keys=[related_lesson_id])
    related_payment = db.relationship('Payment', foreign_keys=[related_payment_id])
    related_makeup = db.relationship('MakeupLesson', foreign_keys=[related_makeup_id])

    def __repr__(self):
        return f'<ScheduledNotification {self.notification_type} - {self.status}>'

    __table_args__ = (
        db.Index('idx_notification_status_scheduled', 'status', 'scheduled_for'),
        db.Index('idx_notification_type', 'notification_type'),
    )


class Discount(db.Model):
    """Descontos configuráveis - Sistema de descontos completo"""
    __tablename__ = 'discounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    
    # Condições de aplicação
    condition_type = db.Column(db.String(50))  # attendance_rate, early_payment, sibling, veteran, special
    condition_value = db.Column(db.Float)  # Ex: 95 para 95% de presença
    
    # Período de validade
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    
    # Aplicação automática
    auto_apply = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Controle
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    creator = db.relationship('User', backref=db.backref('created_discounts', lazy='dynamic'))

    def __repr__(self):
        return f'<Discount {self.name} - {self.discount_value}>'

    __table_args__ = (
        db.Index('idx_discount_active', 'is_active'),
        db.CheckConstraint('discount_value > 0', name='check_positive_discount_value'),
    )


# ============================================================================
# NOVOS MODELOS - LANDING PAGE DINÂMICA E RECITALS COMPLETOS
# ============================================================================

class LandingPageContent(db.Model):
    """Conteúdo editável da Landing Page"""
    __tablename__ = 'landing_page_content'

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), unique=True, nullable=False, index=True)  # hero, about, features, cta
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(500))
    content = db.Column(db.Text)
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    editor = db.relationship('User', backref=db.backref('landing_page_edits', lazy='dynamic'))

    def __repr__(self):
        return f'<LandingPageContent {self.section}>'


class LandingPageFeature(db.Model):
    """Features/Cards da Landing Page"""
    __tablename__ = 'landing_page_features'

    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(100))  # Font Awesome icon class
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<LandingPageFeature {self.title}>'

    __table_args__ = (
        db.Index('idx_feature_active_order', 'is_active', 'display_order'),
    )


class RecitalInvitation(db.Model):
    """Convites automáticos para recitais"""
    __tablename__ = 'recital_invitations'

    id = db.Column(db.Integer, primary_key=True)
    recital_id = db.Column(db.Integer, db.ForeignKey('recitals.id', ondelete='CASCADE'), nullable=False, index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('recital_participants.id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    invitation_token = db.Column(db.String(100), unique=True, index=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, sent, confirmed, declined
    sent_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recital = db.relationship('Recital', backref=db.backref('invitations', lazy='dynamic'))
    participant = db.relationship('RecitalParticipant', backref=db.backref('invitation', uselist=False))

    def __repr__(self):
        return f'<RecitalInvitation {self.email} - {self.status}>'

    __table_args__ = (
        db.Index('idx_invitation_status', 'status'),
        db.Index('idx_invitation_recital', 'recital_id'),
    )


class RecitalCertificate(db.Model):
    """Certificados de participação em recitais"""
    __tablename__ = 'recital_certificates'

    id = db.Column(db.Integer, primary_key=True)
    recital_id = db.Column(db.Integer, db.ForeignKey('recitals.id', ondelete='CASCADE'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('recital_participants.id', ondelete='CASCADE'), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    file_path = db.Column(db.String(500))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    downloaded_at = db.Column(db.DateTime)
    download_count = db.Column(db.Integer, default=0)

    recital = db.relationship('Recital', backref=db.backref('certificates', lazy='dynamic'))
    participant = db.relationship('RecitalParticipant', backref=db.backref('certificate', uselist=False))

    def __repr__(self):
        return f'<RecitalCertificate {self.certificate_number}>'


class SystemAnalytics(db.Model):
    """Analytics do sistema para dashboard macro"""
    __tablename__ = 'system_analytics'

    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False, index=True)  # revenue, students, lessons, attendance
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float)
    value_json = db.Column(db.JSON)  # Para dados complexos
    period_type = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    period_start = db.Column(db.Date, nullable=False, index=True)
    period_end = db.Column(db.Date, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<SystemAnalytics {self.metric_type} - {self.period_start}>'

    __table_args__ = (
        db.Index('idx_analytics_type_period', 'metric_type', 'period_start'),
    )
