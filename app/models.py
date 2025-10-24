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
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, *roles):
        return self.role in roles
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    instrument = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200))
    bio = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))
    availabilities = db.relationship('TeacherAvailability', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    instrument = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(50))
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Dados do Responsável
    guardian_name = db.Column(db.String(200))
    guardian_phone = db.Column(db.String(20))
    guardian_email = db.Column(db.String(120))
    guardian_cpf = db.Column(db.String(14))
    
    # Dados Pessoais
    birth_date = db.Column(db.Date)
    cpf = db.Column(db.String(14))
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
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    lessons = db.relationship('LessonSchedule', backref='student', lazy='dynamic')

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    capacity = db.Column(db.Integer, default=1)
    equipment = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    
    schedules = db.relationship('LessonSchedule', backref='room', lazy='dynamic')

class TeacherAvailability(db.Model):
    __tablename__ = 'teacher_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_recurring = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.Index('idx_teacher_day', 'teacher_id', 'day_of_week'),
    )

class LessonSchedule(db.Model):
    __tablename__ = 'lesson_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    lesson_type = db.Column(db.String(20), default='regular')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teacher = db.relationship('Teacher', backref=db.backref('lessons', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_lesson_date', 'lesson_date'),
        db.Index('idx_teacher_date', 'teacher_id', 'lesson_date'),
    )

class MakeupLesson(db.Model):
    __tablename__ = 'makeup_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    original_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id'), nullable=False)
    new_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson_schedule.id'))
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    original_lesson = db.relationship('LessonSchedule', foreign_keys=[original_lesson_id])
    new_lesson = db.relationship('LessonSchedule', foreign_keys=[new_lesson_id])
    requester = db.relationship('User', foreign_keys=[requested_by])
    approver = db.relationship('User', foreign_keys=[approved_by])

class Recital(db.Model):
    __tablename__ = 'recitals'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='planned')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', backref=db.backref('created_recitals', lazy='dynamic'))
    performances = db.relationship('RecitalPerformance', backref='recital', lazy='dynamic', cascade='all, delete-orphan')

class RecitalPerformance(db.Model):
    __tablename__ = 'recital_performances'
    
    id = db.Column(db.Integer, primary_key=True)
    recital_id = db.Column(db.Integer, db.ForeignKey('recitals.id'), nullable=False)
    performance_type = db.Column(db.String(50), nullable=False)
    piece_title = db.Column(db.String(200), nullable=False)
    composer = db.Column(db.String(200))
    duration_minutes = db.Column(db.Integer)
    order_number = db.Column(db.Integer)
    
    participants = db.relationship('RecitalParticipant', backref='performance', lazy='dynamic', cascade='all, delete-orphan')

class RecitalParticipant(db.Model):
    __tablename__ = 'recital_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    performance_id = db.Column(db.Integer, db.ForeignKey('recital_performances.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    role = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean, default=False)
    
    student = db.relationship('Student', backref=db.backref('recital_participations', lazy='dynamic'))
    teacher = db.relationship('Teacher', backref=db.backref('recital_participations', lazy='dynamic'))

class NewsPost(db.Model):
    __tablename__ = 'news_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type = db.Column(db.String(20), default='news')
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    author = db.relationship('User', backref=db.backref('news_posts', lazy='dynamic'))

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
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    monthly_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref=db.backref('enrollments', lazy='dynamic'))
    payments = db.relationship('Payment', backref='enrollment', lazy='dynamic', cascade='all, delete-orphan')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    reference_month = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    late_fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    receipt_number = db.Column(db.String(50), unique=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_payment_status', 'status'),
        db.Index('idx_payment_due_date', 'due_date'),
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
    category = db.Column(db.String(50), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    related_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy='dynamic'))
    related_student = db.relationship('Student', backref=db.backref('documents', lazy='dynamic'))
    related_teacher = db.relationship('Teacher', backref=db.backref('documents', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_document_category', 'category'),
    )
