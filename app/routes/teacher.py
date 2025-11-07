from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Teacher, TeacherAvailability, LessonSchedule, Student, ScheduledNotification
from datetime import datetime, timedelta, time
from sqlalchemy import func, and_, or_

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


@bp.route('/lessons')
@login_required
@teacher_required
def lessons():
    """Lista de aulas para gerenciar presença e notas"""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash('Perfil de professor não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    # Filtros
    date_filter = request.args.get('date', 'today')
    status_filter = request.args.get('status', 'all')
    
    today = datetime.now().date()
    
    query = LessonSchedule.query.filter(LessonSchedule.teacher_id == teacher.id)
    
    # Aplicar filtro de data
    if date_filter == 'today':
        query = query.filter(LessonSchedule.lesson_date == today)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        query = query.filter(
            LessonSchedule.lesson_date >= week_start,
            LessonSchedule.lesson_date <= week_end
        )
    elif date_filter == 'month':
        query = query.filter(
            func.extract('month', LessonSchedule.lesson_date) == today.month,
            func.extract('year', LessonSchedule.lesson_date) == today.year
        )
    
    # Aplicar filtro de status
    if status_filter != 'all':
        query = query.filter(LessonSchedule.status == status_filter)
    
    lessons = query.order_by(
        LessonSchedule.lesson_date.desc(),
        LessonSchedule.start_time.desc()
    ).all()
    
    return render_template('teacher/lessons.html', 
                         teacher=teacher, 
                         lessons=lessons,
                         date_filter=date_filter,
                         status_filter=status_filter)


@bp.route('/lessons/<int:lesson_id>/attendance', methods=['POST'])
@login_required
@teacher_required
def confirm_attendance(lesson_id):
    """Confirmar presença ou marcar falta de um aluno"""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    lesson = LessonSchedule.query.get_or_404(lesson_id)
    
    # Verificar se a aula pertence ao professor
    if lesson.teacher_id != teacher.id:
        flash('Você não tem permissão para modificar esta aula.', 'error')
        return redirect(url_for('teacher.lessons'))
    
    try:
        attendance_status = request.form.get('attendance_status')
        
        lesson.attendance_status = attendance_status
        lesson.attendance_confirmed = True
        lesson.confirmed_by = current_user.id
        lesson.confirmed_at = datetime.utcnow()
        
        # Atualizar status da aula
        if attendance_status == 'present':
            lesson.status = 'completed'
        elif attendance_status == 'absent':
            lesson.status = 'absent'
        elif attendance_status == 'late':
            lesson.status = 'completed'
        elif attendance_status == 'justified':
            lesson.status = 'cancelled'
        
        db.session.commit()
        
        # Enviar notificação ao aluno
        if attendance_status == 'absent':
            create_absence_notification(lesson)
        
        flash('Presença registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar presença: {str(e)}', 'error')
    
    return redirect(url_for('teacher.lessons'))


@bp.route('/lessons/<int:lesson_id>/notes', methods=['GET', 'POST'])
@login_required
@teacher_required
def lesson_notes(lesson_id):
    """Adicionar ou editar notas da aula"""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    lesson = LessonSchedule.query.get_or_404(lesson_id)
    
    # Verificar se a aula pertence ao professor
    if lesson.teacher_id != teacher.id:
        flash('Você não tem permissão para modificar esta aula.', 'error')
        return redirect(url_for('teacher.lessons'))
    
    if request.method == 'POST':
        try:
            lesson.lesson_notes = request.form.get('lesson_notes')
            lesson.lesson_content = request.form.get('lesson_content')
            lesson.homework_assigned = request.form.get('homework_assigned')
            lesson.student_progress = request.form.get('student_progress')
            
            db.session.commit()
            flash('Notas da aula salvas com sucesso!', 'success')
            return redirect(url_for('teacher.lessons'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar notas: {str(e)}', 'error')
    
    return render_template('teacher/lesson_notes.html', teacher=teacher, lesson=lesson)


@bp.route('/students')
@login_required
@teacher_required
def students():
    """Lista de alunos do professor"""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash('Perfil de professor não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    # Buscar alunos únicos que tem aulas com este professor
    students_query = db.session.query(Student).join(
        LessonSchedule, Student.id == LessonSchedule.student_id
    ).filter(
        LessonSchedule.teacher_id == teacher.id
    ).distinct()
    
    students = students_query.all()
    
    # Calcular estatísticas para cada aluno
    student_stats = []
    for student in students:
        total_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student.id,
            LessonSchedule.teacher_id == teacher.id,
            LessonSchedule.status.in_(['completed', 'absent'])
        ).count()
        
        present_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student.id,
            LessonSchedule.teacher_id == teacher.id,
            LessonSchedule.attendance_status == 'present'
        ).count()
        
        attendance_rate = (present_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        student_stats.append({
            'student': student,
            'total_lessons': total_lessons,
            'present_lessons': present_lessons,
            'attendance_rate': round(attendance_rate, 1)
        })
    
    return render_template('teacher/students.html', 
                         teacher=teacher, 
                         student_stats=student_stats)


@bp.route('/students/<int:student_id>/history')
@login_required
@teacher_required
def student_history(student_id):
    """Histórico de aulas de um aluno específico"""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    student = Student.query.get_or_404(student_id)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.student_id == student_id,
        LessonSchedule.teacher_id == teacher.id
    ).order_by(LessonSchedule.lesson_date.desc()).all()
    
    return render_template('teacher/student_history.html', 
                         teacher=teacher, 
                         student=student,
                         lessons=lessons)


def create_absence_notification(lesson):
    """Criar notificação de falta para o aluno"""
    try:
        notification = ScheduledNotification(
            notification_type='absence_alert',
            recipient_id=lesson.student.user_id,
            recipient_email=lesson.student.user.email,
            subject='Falta registrada em sua aula',
            message=f'Olá {lesson.student.user.full_name},\n\n'
                   f'Registramos sua falta na aula do dia {lesson.lesson_date.strftime("%d/%m/%Y")} '
                   f'às {lesson.start_time.strftime("%H:%M")}.\n\n'
                   f'Caso tenha sido um erro ou você tenha uma justificativa, '
                   f'por favor entre em contato com a secretaria.\n\n'
                   f'Atenciosamente,\nEscola de Música Solmaior',
            related_lesson_id=lesson.id,
            scheduled_for=datetime.utcnow(),
            status='pending'
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        print(f'Erro ao criar notificação de falta: {str(e)}')
