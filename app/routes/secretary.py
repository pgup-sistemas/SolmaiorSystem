from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Teacher, Student, LessonSchedule, Room, MakeupLesson, TeacherAvailability
from datetime import datetime, timedelta

bp = Blueprint('secretary', __name__, url_prefix='/secretary')

def secretary_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['secretary', 'admin']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@secretary_required
def dashboard():
    today = datetime.now().date()
    todays_lessons = LessonSchedule.query.filter_by(lesson_date=today).count()
    pending_makeups = MakeupLesson.query.filter_by(status='pending').count()
    
    return render_template('secretary/dashboard.html',
                         todays_lessons=todays_lessons,
                         pending_makeups=pending_makeups)

@bp.route('/schedule')
@login_required
@secretary_required
def schedule():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.lesson_date >= week_start,
        LessonSchedule.lesson_date <= week_end
    ).all()
    
    teachers = Teacher.query.all()
    students = Student.query.all()
    rooms = Room.query.all()
    
    return render_template('secretary/schedule.html',
                         lessons=lessons,
                         teachers=teachers,
                         students=students,
                         rooms=rooms,
                         week_start=week_start)

@bp.route('/schedule/create', methods=['POST'])
@login_required
@secretary_required
def create_schedule():
    lesson = LessonSchedule(
        teacher_id=request.form.get('teacher_id', type=int),
        student_id=request.form.get('student_id', type=int),
        room_id=request.form.get('room_id', type=int),
        lesson_date=datetime.strptime(request.form.get('lesson_date'), '%Y-%m-%d').date(),
        start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
        end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
        notes=request.form.get('notes')
    )
    
    conflicts = LessonSchedule.query.filter(
        LessonSchedule.lesson_date == lesson.lesson_date,
        LessonSchedule.teacher_id == lesson.teacher_id,
        LessonSchedule.start_time < lesson.end_time,
        LessonSchedule.end_time > lesson.start_time
    ).first()
    
    if conflicts:
        flash('Conflito de horário detectado com outra aula do professor!', 'error')
        return redirect(url_for('secretary.schedule'))
    
    room_conflicts = LessonSchedule.query.filter(
        LessonSchedule.lesson_date == lesson.lesson_date,
        LessonSchedule.room_id == lesson.room_id,
        LessonSchedule.start_time < lesson.end_time,
        LessonSchedule.end_time > lesson.start_time
    ).first()
    
    if room_conflicts:
        flash('Conflito de horário detectado na sala!', 'error')
        return redirect(url_for('secretary.schedule'))
    
    db.session.add(lesson)
    db.session.commit()
    
    flash('Aula agendada com sucesso!', 'success')
    return redirect(url_for('secretary.schedule'))

@bp.route('/makeups')
@login_required
@secretary_required
def makeups():
    makeups = MakeupLesson.query.order_by(MakeupLesson.created_at.desc()).all()
    return render_template('secretary/makeups.html', makeups=makeups)

@bp.route('/makeups/create', methods=['POST'])
@login_required
@secretary_required
def create_makeup():
    makeup = MakeupLesson(
        original_lesson_id=request.form.get('original_lesson_id', type=int),
        reason=request.form.get('reason'),
        requested_by=current_user.id,
        status='pending'
    )
    
    db.session.add(makeup)
    db.session.commit()
    
    flash('Reposição registrada com sucesso!', 'success')
    return redirect(url_for('secretary.makeups'))
