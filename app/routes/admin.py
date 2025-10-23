from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Teacher, Student, Room, LessonSchedule, Recital, NewsPost, TrialLesson, TeacherAvailability
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_rooms = Room.query.count()
    pending_trials = TrialLesson.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_rooms=total_rooms,
                         pending_trials=pending_trials)

@bp.route('/global-schedule')
@login_required
@admin_required
def global_schedule():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.lesson_date >= week_start,
        LessonSchedule.lesson_date <= week_end
    ).all()
    
    teachers = Teacher.query.all()
    rooms = Room.query.all()
    
    return render_template('admin/global_schedule.html',
                         lessons=lessons,
                         teachers=teachers,
                         rooms=rooms,
                         week_start=week_start)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role')
        
        if not email or not password or not full_name or not role:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return redirect(url_for('admin.create_user'))
        
        try:
            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()
            
            if role == 'teacher':
                teacher = Teacher(
                    user_id=user.id,
                    instrument=request.form.get('instrument', 'Não especificado'),
                    specialization=request.form.get('specialization', '')
                )
                db.session.add(teacher)
            elif role == 'student':
                student = Student(
                    user_id=user.id,
                    instrument=request.form.get('instrument', 'Não especificado'),
                    level=request.form.get('level', 'Iniciante')
                )
                db.session.add(student)
            
            db.session.commit()
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
            return redirect(url_for('admin.create_user'))
    
    return render_template('admin/create_user.html')

@bp.route('/rooms')
@login_required
@admin_required
def rooms():
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)

@bp.route('/rooms/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_room():
    if request.method == 'POST':
        room = Room(
            name=request.form.get('name'),
            capacity=request.form.get('capacity', type=int),
            equipment=request.form.get('equipment')
        )
        
        db.session.add(room)
        db.session.commit()
        
        flash('Sala criada com sucesso!', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/create_room.html')

@bp.route('/recitals')
@login_required
@admin_required
def recitals():
    recitals = Recital.query.order_by(Recital.event_date.desc()).all()
    return render_template('admin/recitals.html', recitals=recitals)

@bp.route('/recitals/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_recital():
    if request.method == 'POST':
        recital = Recital(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M'),
            location=request.form.get('location'),
            created_by=current_user.id
        )
        
        db.session.add(recital)
        db.session.commit()
        
        flash('Recital criado com sucesso!', 'success')
        return redirect(url_for('admin.recitals'))
    
    return render_template('admin/create_recital.html')

@bp.route('/news')
@login_required
@admin_required
def news():
    posts = NewsPost.query.order_by(NewsPost.created_at.desc()).all()
    return render_template('admin/news.html', posts=posts)

@bp.route('/news/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_news():
    if request.method == 'POST':
        post = NewsPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author_id=current_user.id,
            post_type=request.form.get('post_type', 'news'),
            is_published=request.form.get('is_published') == 'on'
        )
        
        if post.is_published:
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Notícia criada com sucesso!', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/create_news.html')

@bp.route('/trial-lessons')
@login_required
@admin_required
def trial_lessons():
    trials = TrialLesson.query.order_by(TrialLesson.created_at.desc()).all()
    return render_template('admin/trial_lessons.html', trials=trials)
