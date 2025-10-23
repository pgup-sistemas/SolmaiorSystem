from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Teacher, TeacherAvailability, LessonSchedule
from datetime import datetime, timedelta, time

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash('Perfil de professor não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    today = datetime.now().date()
    upcoming_lessons = LessonSchedule.query.filter(
        LessonSchedule.teacher_id == teacher.id,
        LessonSchedule.lesson_date >= today
    ).order_by(LessonSchedule.lesson_date, LessonSchedule.start_time).limit(10).all()
    
    return render_template('teacher/dashboard.html', teacher=teacher, upcoming_lessons=upcoming_lessons)

@bp.route('/availability')
@login_required
@teacher_required
def availability():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    availabilities = TeacherAvailability.query.filter_by(teacher_id=teacher.id).all()
    
    return render_template('teacher/availability.html', teacher=teacher, availabilities=availabilities)

@bp.route('/availability/create', methods=['POST'])
@login_required
@teacher_required
def create_availability():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    availability = TeacherAvailability(
        teacher_id=teacher.id,
        day_of_week=int(request.form.get('day_of_week')),
        start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
        end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time()
    )
    
    db.session.add(availability)
    db.session.commit()
    
    flash('Disponibilidade adicionada com sucesso!', 'success')
    return redirect(url_for('teacher.availability'))

@bp.route('/availability/<int:id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_availability(id):
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    availability = TeacherAvailability.query.get_or_404(id)
    
    if availability.teacher_id != teacher.id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('teacher.availability'))
    
    db.session.delete(availability)
    db.session.commit()
    
    flash('Disponibilidade removida com sucesso!', 'success')
    return redirect(url_for('teacher.availability'))

@bp.route('/schedule')
@login_required
@teacher_required
def schedule():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.teacher_id == teacher.id,
        LessonSchedule.lesson_date >= week_start,
        LessonSchedule.lesson_date <= week_end
    ).all()
    
    return render_template('teacher/schedule.html', teacher=teacher, lessons=lessons, week_start=week_start)
