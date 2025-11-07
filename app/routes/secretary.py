from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (Teacher, Student, LessonSchedule, Room, MakeupLesson, TeacherAvailability, 
                        LessonWaitlist, ScheduledNotification, User)
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

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


@bp.route('/makeups/<int:makeup_id>/approve', methods=['POST'])
@login_required
@secretary_required
def approve_makeup(makeup_id):
    """Aprovar solicitação de reposição"""
    makeup = MakeupLesson.query.get_or_404(makeup_id)
    
    if makeup.status != 'pending':
        flash('Esta reposição já foi processada.', 'warning')
        return redirect(url_for('secretary.makeups'))
    
    try:
        # Criar nova aula de reposição se fornecida
        new_lesson_date = request.form.get('new_lesson_date')
        new_lesson_time = request.form.get('new_lesson_time')
        room_id = request.form.get('room_id', type=int)
        
        if new_lesson_date and new_lesson_time:
            # Criar nova aula agendada
            original_lesson = makeup.original_lesson
            
            new_lesson = LessonSchedule(
                teacher_id=original_lesson.teacher_id,
                student_id=original_lesson.student_id,
                room_id=room_id or original_lesson.room_id,
                lesson_date=datetime.strptime(new_lesson_date, '%Y-%m-%d').date(),
                start_time=datetime.strptime(new_lesson_time, '%H:%M').time(),
                end_time=(datetime.strptime(new_lesson_time, '%H:%M') + timedelta(hours=1)).time(),
                lesson_type='makeup',
                status='scheduled'
            )
            
            # Verificar conflitos
            conflicts = LessonSchedule.query.filter(
                LessonSchedule.lesson_date == new_lesson.lesson_date,
                LessonSchedule.teacher_id == new_lesson.teacher_id,
                LessonSchedule.start_time < new_lesson.end_time,
                LessonSchedule.end_time > new_lesson.start_time
            ).first()
            
            if conflicts:
                flash('Conflito de horário detectado!', 'error')
                return redirect(url_for('secretary.makeups'))
            
            db.session.add(new_lesson)
            db.session.flush()
            
            makeup.new_lesson_id = new_lesson.id
            makeup.status = 'scheduled'
        else:
            makeup.status = 'approved'
        
        makeup.approved_by = current_user.id
        
        # Enviar notificação ao aluno
        create_makeup_notification(makeup, 'approved')
        
        db.session.commit()
        flash('Reposição aprovada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar reposição: {str(e)}', 'error')
    
    return redirect(url_for('secretary.makeups'))


@bp.route('/makeups/<int:makeup_id>/reject', methods=['POST'])
@login_required
@secretary_required
def reject_makeup(makeup_id):
    """Rejeitar solicitação de reposição"""
    makeup = MakeupLesson.query.get_or_404(makeup_id)
    
    if makeup.status != 'pending':
        flash('Esta reposição já foi processada.', 'warning')
        return redirect(url_for('secretary.makeups'))
    
    try:
        makeup.status = 'rejected'
        makeup.approved_by = current_user.id
        
        # Enviar notificação ao aluno
        create_makeup_notification(makeup, 'rejected')
        
        db.session.commit()
        flash('Reposição rejeitada.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao rejeitar reposição: {str(e)}', 'error')
    
    return redirect(url_for('secretary.makeups'))


@bp.route('/global-schedule')
@login_required
@secretary_required
def global_schedule():
    """Agenda global - todas as aulas"""
    # Filtros
    date_filter = request.args.get('date', 'week')
    teacher_filter = request.args.get('teacher_id', type=int)
    room_filter = request.args.get('room_id', type=int)
    
    today = datetime.now().date()
    
    query = LessonSchedule.query
    
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
    
    # Aplicar filtros opcionais
    if teacher_filter:
        query = query.filter(LessonSchedule.teacher_id == teacher_filter)
    if room_filter:
        query = query.filter(LessonSchedule.room_id == room_filter)
    
    lessons = query.order_by(
        LessonSchedule.lesson_date,
        LessonSchedule.start_time
    ).all()
    
    teachers = Teacher.query.all()
    rooms = Room.query.all()
    
    return render_template('secretary/global_schedule.html',
                         lessons=lessons,
                         teachers=teachers,
                         rooms=rooms,
                         date_filter=date_filter,
                         teacher_filter=teacher_filter,
                         room_filter=room_filter)


@bp.route('/waitlist')
@login_required
@secretary_required
def waitlist():
    """Gestão de fila de espera"""
    status_filter = request.args.get('status', 'waiting')
    
    query = LessonWaitlist.query
    if status_filter != 'all':
        query = query.filter(LessonWaitlist.status == status_filter)
    
    waitlist_entries = query.order_by(
        LessonWaitlist.priority,
        LessonWaitlist.created_at
    ).all()
    
    teachers = Teacher.query.all()
    
    return render_template('secretary/waitlist.html',
                         waitlist_entries=waitlist_entries,
                         teachers=teachers,
                         status_filter=status_filter)


@bp.route('/waitlist/create', methods=['POST'])
@login_required
@secretary_required
def create_waitlist_entry():
    """Adicionar aluno à fila de espera"""
    try:
        # Calcular próxima prioridade
        max_priority = db.session.query(func.max(LessonWaitlist.priority)).scalar() or 0
        
        waitlist_entry = LessonWaitlist(
            student_id=request.form.get('student_id', type=int),
            teacher_id=request.form.get('teacher_id', type=int),
            instrument=request.form.get('instrument'),
            preferred_day=request.form.get('preferred_day'),
            preferred_time=request.form.get('preferred_time'),
            duration=request.form.get('duration', type=int, default=60),
            priority=max_priority + 1,
            status='waiting',
            expires_at=datetime.utcnow() + timedelta(days=30),
            notes=request.form.get('notes')
        )
        
        db.session.add(waitlist_entry)
        db.session.commit()
        
        flash('Aluno adicionado à fila de espera!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar à fila: {str(e)}', 'error')
    
    return redirect(url_for('secretary.waitlist'))


@bp.route('/waitlist/<int:entry_id>/match', methods=['POST'])
@login_required
@secretary_required
def match_waitlist(entry_id):
    """Marcar entrada da fila como atendida"""
    entry = LessonWaitlist.query.get_or_404(entry_id)
    
    try:
        entry.status = 'matched'
        entry.matched_at = datetime.utcnow()
        
        # Enviar notificação ao aluno
        notification = ScheduledNotification(
            notification_type='waitlist_matched',
            recipient_id=entry.student.user_id,
            recipient_email=entry.student.user.email,
            subject='Vaga disponível!',
            message=f'Olá {entry.student.user.full_name},\n\n'
                   f'Temos uma vaga disponível para suas aulas de {entry.instrument}!\n\n'
                   f'Por favor, entre em contato com a secretaria para agendar seu horário.\n\n'
                   f'Atenciosamente,\nEscola de Música Solmaior',
            scheduled_for=datetime.utcnow(),
            status='pending'
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Entrada marcada como atendida!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao processar: {str(e)}', 'error')
    
    return redirect(url_for('secretary.waitlist'))


@bp.route('/waitlist/<int:entry_id>/cancel', methods=['POST'])
@login_required
@secretary_required
def cancel_waitlist(entry_id):
    """Cancelar entrada da fila"""
    entry = LessonWaitlist.query.get_or_404(entry_id)
    
    try:
        entry.status = 'cancelled'
        db.session.commit()
        flash('Entrada cancelada.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar: {str(e)}', 'error')
    
    return redirect(url_for('secretary.waitlist'))


def create_makeup_notification(makeup, action):
    """Criar notificação sobre reposição"""
    try:
        student = makeup.original_lesson.student
        
        if action == 'approved':
            subject = 'Reposição aprovada'
            if makeup.new_lesson:
                message = f'Olá {student.user.full_name},\n\n'\
                         f'Sua reposição foi aprovada e agendada para '\
                         f'{makeup.new_lesson.lesson_date.strftime("%d/%m/%Y")} '\
                         f'às {makeup.new_lesson.start_time.strftime("%H:%M")}.\n\n'\
                         f'Atenciosamente,\nEscola de Música Solmaior'
            else:
                message = f'Olá {student.user.full_name},\n\n'\
                         f'Sua solicitação de reposição foi aprovada. '\
                         f'Em breve entraremos em contato para agendar.\n\n'\
                         f'Atenciosamente,\nEscola de Música Solmaior'
        else:  # rejected
            subject = 'Reposição não aprovada'
            message = f'Olá {student.user.full_name},\n\n'\
                     f'Infelizmente sua solicitação de reposição não foi aprovada. '\
                     f'Motivo: {request.form.get("rejection_reason", "não especificado")}.\n\n'\
                     f'Para mais informações, entre em contato com a secretaria.\n\n'\
                     f'Atenciosamente,\nEscola de Música Solmaior'
        
        notification = ScheduledNotification(
            notification_type=f'makeup_{action}',
            recipient_id=student.user_id,
            recipient_email=student.user.email,
            subject=subject,
            message=message,
            related_makeup_id=makeup.id,
            scheduled_for=datetime.utcnow(),
            status='pending'
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        print(f'Erro ao criar notificação: {str(e)}')
