from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Student, LessonSchedule
from datetime import datetime, timedelta

bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Perfil de aluno não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    today = datetime.now().date()
    upcoming_lessons = LessonSchedule.query.filter(
        LessonSchedule.student_id == student.id,
        LessonSchedule.lesson_date >= today
    ).order_by(LessonSchedule.lesson_date, LessonSchedule.start_time).limit(10).all()
    
    return render_template('student/dashboard.html', student=student, upcoming_lessons=upcoming_lessons)

@bp.route('/schedule')
@login_required
@student_required
def schedule():
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    today = datetime.now().date()
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.student_id == student.id,
        LessonSchedule.lesson_date >= month_start,
        LessonSchedule.lesson_date <= month_end
    ).all()
    
    return render_template('student/schedule.html', student=student, lessons=lessons)
