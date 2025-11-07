from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Student, LessonSchedule, Enrollment, Payment, Recital, RecitalParticipant, RecitalPerformance, MakeupLesson
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io

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
    ).order_by(LessonSchedule.lesson_date, LessonSchedule.start_time).limit(5).all()
    
    # Informações financeiras resumidas
    enrollment = Enrollment.query.filter_by(student_id=student.id, status='active').first()
    next_payment = None
    payment_status = None
    
    if enrollment:
        next_payment = Payment.query.filter_by(
            enrollment_id=enrollment.id,
            status='pending'
        ).order_by(Payment.due_date).first()
        
        if next_payment:
            if next_payment.due_date < today:
                payment_status = 'overdue'
            elif next_payment.due_date <= today + timedelta(days=7):
                payment_status = 'due_soon'
            else:
                payment_status = 'ok'
    
    # Próximos recitais
    upcoming_recitals = db.session.query(Recital).select_from(Recital).join(
        RecitalPerformance, 
        RecitalPerformance.recital_id == Recital.id
    ).join(
        RecitalParticipant,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalParticipant.student_id == student.id,
        db.func.date(Recital.event_date) >= today,
        Recital.status.in_(['planejado', 'confirmado', 'planned', 'confirmed'])
    ).order_by(Recital.event_date).limit(2).all()
    
    # Taxa de frequência do mês
    month_start = today.replace(day=1)
    month_lessons = LessonSchedule.query.filter(
        LessonSchedule.student_id == student.id,
        LessonSchedule.lesson_date >= month_start,
        LessonSchedule.lesson_date < today
    ).all()
    
    if month_lessons:
        attended = len([l for l in month_lessons if l.status in ['realizada', 'completed']])
        attendance_rate = int((attended / len(month_lessons)) * 100)
    else:
        attendance_rate = 100
    
    return render_template('student/dashboard.html', 
                         student=student, 
                         upcoming_lessons=upcoming_lessons,
                         next_payment=next_payment,
                         payment_status=payment_status,
                         upcoming_recitals=upcoming_recitals,
                         attendance_rate=attendance_rate)

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

@bp.route('/financial')
@login_required
@student_required
def financial():
    """Área financeira do aluno"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Perfil de aluno não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    # Matrícula ativa
    enrollment = Enrollment.query.filter_by(student_id=student.id, status='active').first()
    
    if not enrollment:
        return render_template('student/financial.html', 
                             student=student, 
                             enrollment=None,
                             payments=[],
                             payment_summary={})
    
    # Todos os pagamentos
    payments = Payment.query.filter_by(enrollment_id=enrollment.id).order_by(Payment.due_date.desc()).all()
    
    # Resumo financeiro
    total_paid = sum(p.total_amount for p in payments if p.status == 'paid')
    total_pending = sum(p.amount for p in payments if p.status == 'pending')
    overdue_count = len([p for p in payments if p.status == 'pending' and p.due_date < datetime.now().date()])
    
    payment_summary = {
        'total_paid': total_paid,
        'total_pending': total_pending,
        'overdue_count': overdue_count,
        'monthly_value': enrollment.monthly_value
    }
    
    return render_template('student/financial.html',
                         student=student,
                         enrollment=enrollment,
                         payments=payments,
                         payment_summary=payment_summary,
                         today=datetime.now().date())

@bp.route('/financial/receipt/<int:payment_id>')
@login_required
@student_required
def download_receipt(payment_id):
    """Download de recibo de pagamento"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    payment = Payment.query.get_or_404(payment_id)
    
    # Verificar se o pagamento pertence ao aluno
    if payment.enrollment.student_id != student.id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('student.financial'))
    
    if payment.status != 'paid':
        flash('Este pagamento ainda não foi realizado.', 'error')
        return redirect(url_for('student.financial'))
    
    # Gerar recibo simples (sem reportlab por enquanto)
    try:
        from app.services import generate_simple_receipt
        pdf_buffer = generate_simple_receipt(payment)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'recibo_{payment.receipt_number or payment.id}.pdf'
        )
    except Exception as e:
        flash(f'Erro ao gerar recibo: {str(e)}', 'error')
        return redirect(url_for('student.financial'))

@bp.route('/recitals')
@login_required
@student_required
def recitals():
    """Lista de recitais e eventos do aluno"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Perfil de aluno não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    today = datetime.now().date()
    
    # Recitais futuros
    upcoming = db.session.query(Recital).select_from(Recital).join(
        RecitalPerformance, 
        RecitalPerformance.recital_id == Recital.id
    ).join(
        RecitalParticipant,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalParticipant.student_id == student.id,
        db.func.date(Recital.event_date) >= today
    ).order_by(Recital.event_date).all()
    
    # Recitais passados
    past = db.session.query(Recital).select_from(Recital).join(
        RecitalPerformance, 
        RecitalPerformance.recital_id == Recital.id
    ).join(
        RecitalParticipant,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalParticipant.student_id == student.id,
        db.func.date(Recital.event_date) < today
    ).order_by(Recital.event_date.desc()).all()
    
    return render_template('student/recitals.html',
                         student=student,
                         upcoming_recitals=upcoming,
                         past_recitals=past)

@bp.route('/recitals/<int:recital_id>')
@login_required
@student_required
def recital_detail(recital_id):
    """Detalhes de um recital específico"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    recital = Recital.query.get_or_404(recital_id)
    
    # Verificar se o aluno participa deste recital (através de RecitalPerformance)
    participant = db.session.query(RecitalParticipant).join(
        RecitalPerformance,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalPerformance.recital_id == recital_id,
        RecitalParticipant.student_id == student.id
    ).first()
    
    if not participant:
        flash('Você não está inscrito neste evento.', 'error')
        return redirect(url_for('student.recitals'))
    
    # Buscar apresentações do aluno neste recital
    performances = RecitalPerformance.query.filter_by(recital_id=recital_id).all()
    student_performances = [p for p in performances if student.id in [sp.student_id for sp in p.participants]]
    
    return render_template('student/recital_detail.html',
                         student=student,
                         recital=recital,
                         participant=participant,
                         performances=student_performances)

@bp.route('/recitals/<int:recital_id>/confirm', methods=['POST'])
@login_required
@student_required
def confirm_recital(recital_id):
    """Confirmar presença em recital"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    participant = db.session.query(RecitalParticipant).join(
        RecitalPerformance,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalPerformance.recital_id == recital_id,
        RecitalParticipant.student_id == student.id
    ).first_or_404()
    
    participant.confirmed = True
    
    db.session.commit()
    flash('Presença confirmada com sucesso!', 'success')
    return redirect(url_for('student.recital_detail', recital_id=recital_id))

@bp.route('/recitals/<int:recital_id>/decline', methods=['POST'])
@login_required
@student_required
def decline_recital(recital_id):
    """Declinar participação em recital"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    participant = db.session.query(RecitalParticipant).join(
        RecitalPerformance,
        RecitalParticipant.performance_id == RecitalPerformance.id
    ).filter(
        RecitalPerformance.recital_id == recital_id,
        RecitalParticipant.student_id == student.id
    ).first_or_404()
    
    participant.confirmed = False
    
    db.session.commit()
    flash('Você declinou a participação neste evento.', 'info')
    return redirect(url_for('student.recitals'))

@bp.route('/makeup-lessons')
@login_required
@student_required
def makeup_lessons():
    """Lista de reposições do aluno"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Perfil de aluno não encontrado.', 'error')
        return redirect(url_for('public.index'))
    
    today = datetime.now().date()
    
    # Aulas passadas que podem ser repostas (canceladas ou faltou)
    eligible_lessons = LessonSchedule.query.filter(
        LessonSchedule.student_id == student.id,
        LessonSchedule.lesson_date < today,
        LessonSchedule.status.in_(['cancelled', 'falta', 'cancelada'])
    ).order_by(LessonSchedule.lesson_date.desc()).limit(20).all()
    
    # Verificar quais já têm solicitação de reposição
    lessons_with_request = []
    lessons_without_request = []
    
    for lesson in eligible_lessons:
        existing_request = MakeupLesson.query.filter_by(original_lesson_id=lesson.id).first()
        if existing_request:
            lessons_with_request.append({
                'lesson': lesson,
                'request': existing_request
            })
        else:
            lessons_without_request.append(lesson)
    
    # Reposições pendentes
    pending_makeups = MakeupLesson.query.join(LessonSchedule, MakeupLesson.original_lesson_id == LessonSchedule.id).filter(
        LessonSchedule.student_id == student.id,
        MakeupLesson.status.in_(['pending', 'approved'])
    ).all()
    
    return render_template('student/makeup_lessons.html',
                         student=student,
                         lessons_without_request=lessons_without_request,
                         lessons_with_request=lessons_with_request,
                         pending_makeups=pending_makeups)

@bp.route('/makeup-lessons/request/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
@student_required
def request_makeup(lesson_id):
    """Solicitar reposição de aula"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    lesson = LessonSchedule.query.get_or_404(lesson_id)
    
    # Verificar se a aula pertence ao aluno
    if lesson.student_id != student.id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('student.makeup_lessons'))
    
    # Verificar se já existe solicitação
    existing = MakeupLesson.query.filter_by(original_lesson_id=lesson_id).first()
    if existing:
        flash('Já existe uma solicitação de reposição para esta aula.', 'info')
        return redirect(url_for('student.makeup_lessons'))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        
        if not reason:
            flash('Por favor, informe o motivo da reposição.', 'error')
            return redirect(request.url)
        
        makeup = MakeupLesson(
            original_lesson_id=lesson_id,
            reason=reason,
            requested_by=current_user.id,
            status='pending'
        )
        
        db.session.add(makeup)
        db.session.commit()
        
        flash('Solicitação de reposição enviada com sucesso!', 'success')
        return redirect(url_for('student.makeup_lessons'))
    
    return render_template('student/request_makeup.html', student=student, lesson=lesson)

@bp.route('/makeup-lessons/<int:makeup_id>/suggestions')
@login_required
@student_required
def makeup_suggestions(makeup_id):
    """Ver sugestões de horários para reposição"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    makeup = MakeupLesson.query.get_or_404(makeup_id)
    
    # Verificar se pertence ao aluno
    if makeup.original_lesson.student_id != student.id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('student.makeup_lessons'))
    
    # Gerar sugestões automáticas (próximos 30 dias)
    from app.services import MakeupLessonService
    suggestions = []
    
    original_lesson = makeup.original_lesson
    today = datetime.now()
    
    # Buscar 5 sugestões de horários
    for i in range(1, 31):
        check_datetime = today + timedelta(days=i)
        check_date = check_datetime.date()
        
        # Mesmo dia da semana, mesmo horário
        if check_date.weekday() == original_lesson.lesson_date.weekday():
            # Verificar disponibilidade
            conflict = LessonSchedule.query.filter(
                db.or_(
                    LessonSchedule.teacher_id == original_lesson.teacher_id,
                    LessonSchedule.student_id == original_lesson.student_id,
                    LessonSchedule.room_id == original_lesson.room_id
                ),
                LessonSchedule.lesson_date == check_date,
                LessonSchedule.start_time == original_lesson.start_time,
                LessonSchedule.status != 'cancelled'
            ).first()
            
            if not conflict:
                suggestions.append({
                    'date': check_date,
                    'start_time': original_lesson.start_time,
                    'end_time': original_lesson.end_time,
                    'teacher': original_lesson.teacher,
                    'room': original_lesson.room,
                    'available': True
                })
            
            if len(suggestions) >= 5:
                break
    
    return render_template('student/makeup_suggestions.html',
                         student=student,
                         makeup=makeup,
                         suggestions=suggestions)

@bp.route('/makeup-lessons/<int:makeup_id>/confirm', methods=['POST'])
@login_required
@student_required
def confirm_makeup(makeup_id):
    """Confirmar horário de reposição sugerido"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    makeup = MakeupLesson.query.get_or_404(makeup_id)
    
    # Verificar permissão
    if makeup.original_lesson.student_id != student.id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('student.makeup_lessons'))
    
    selected_date = request.form.get('selected_date')
    selected_time = request.form.get('selected_time')
    
    if not selected_date or not selected_time:
        flash('Por favor, selecione uma data e horário.', 'error')
        return redirect(url_for('student.makeup_suggestions', makeup_id=makeup_id))
    
    # Criar nova aula de reposição
    original = makeup.original_lesson
    new_lesson = LessonSchedule(
        teacher_id=original.teacher_id,
        student_id=original.student_id,
        room_id=original.room_id,
        lesson_date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
        start_time=datetime.strptime(selected_time, '%H:%M').time(),
        end_time=original.end_time,
        status='scheduled',
        lesson_type='makeup',
        notes=f'Reposição da aula de {original.lesson_date.strftime("%d/%m/%Y")}'
    )
    
    db.session.add(new_lesson)
    db.session.flush()
    
    # Atualizar solicitação de reposição
    makeup.new_lesson_id = new_lesson.id
    makeup.status = 'scheduled'
    
    db.session.commit()
    
    flash('Reposição agendada com sucesso!', 'success')
    return redirect(url_for('student.makeup_lessons'))
