
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
    attendance_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<TrialLesson {self.full_name} - {self.instrument}>'

    __table_args__ = (
        db.Index('idx_trial_status', 'status'),
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
    late_fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, credit_card, debit_card, pix, bank_transfer
    status = db.Column(db.String(20), default='pending', index=True)  # pending, paid, cancelled, refunded
    receipt_number = db.Column(db.String(50), unique=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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
