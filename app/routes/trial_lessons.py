"""
Rotas para gerenciamento de Aulas Experimentais (Trial Lessons)
Admin e Secretaria podem:
- Visualizar solicitações
- Agendar aulas experimentais
- Confirmar/cancelar
- Enviar emails automáticos
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import TrialLesson, Teacher, Room, User
from app.tasks import send_email
from datetime import datetime, date, time
from functools import wraps

bp = Blueprint('trial_lessons', __name__, url_prefix='/trial-lessons')


def admin_or_secretary_required(f):
    """Decorator para permitir apenas admin e secretaria"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['admin', 'secretary']:
            flash('Acesso negado. Apenas administradores e secretaria podem acessar esta área.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@admin_or_secretary_required
def index():
    """Lista todas as solicitações de aulas experimentais"""
    status_filter = request.args.get('status', 'all')
    instrument_filter = request.args.get('instrument', 'all')
    
    query = TrialLesson.query
    
    # Filtros
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if instrument_filter != 'all':
        query = query.filter_by(instrument=instrument_filter)
    
    trial_lessons = query.order_by(TrialLesson.created_at.desc()).all()
    
    # Pegar lista de instrumentos únicos para o filtro
    instruments = db.session.query(TrialLesson.instrument).distinct().all()
    instruments = [i[0] for i in instruments]
    
    # Estatísticas
    stats = {
        'pending': TrialLesson.query.filter_by(status='pending').count(),
        'scheduled': TrialLesson.query.filter_by(status='scheduled').count(),
        'completed': TrialLesson.query.filter_by(status='completed').count(),
        'cancelled': TrialLesson.query.filter_by(status='cancelled').count(),
    }
    
    return render_template('trial_lessons/index.html',
                         trial_lessons=trial_lessons,
                         instruments=instruments,
                         stats=stats,
                         status_filter=status_filter,
                         instrument_filter=instrument_filter)


@bp.route('/<int:id>')
@admin_or_secretary_required
def view(id):
    """Visualizar detalhes de uma solicitação"""
    trial = TrialLesson.query.get_or_404(id)
    teachers = Teacher.query.join(User).filter(User.is_active == True).all()
    rooms = Room.query.filter_by(is_available=True).all()
    
    return render_template('trial_lessons/view.html',
                         trial=trial,
                         teachers=teachers,
                         rooms=rooms,
                         today=date.today())


@bp.route('/<int:id>/schedule', methods=['POST'])
@admin_or_secretary_required
def schedule(id):
    """Agendar uma aula experimental"""
    import secrets
    trial = TrialLesson.query.get_or_404(id)
    
    try:
        # Dados do formulário
        scheduled_date_str = request.form.get('scheduled_date')
        scheduled_time_str = request.form.get('scheduled_time')
        teacher_id = request.form.get('teacher_id')
        room_id = request.form.get('room_id')
        duration = request.form.get('duration_minutes', 60, type=int)
        notes = request.form.get('notes', '')
        
        # Validações
        if not all([scheduled_date_str, scheduled_time_str, teacher_id]):
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('trial_lessons.view', id=id))
        
        # Converter data e hora
        scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M').time()
        
        # Gerar token único para confirmação
        if not trial.confirmation_token:
            trial.confirmation_token = secrets.token_urlsafe(32)
        
        # Atualizar trial lesson
        trial.scheduled_date = scheduled_date
        trial.scheduled_time = scheduled_time
        trial.assigned_teacher_id = teacher_id
        trial.room_id = room_id if room_id else None
        trial.duration_minutes = duration
        trial.notes = notes
        trial.status = 'scheduled'
        
        db.session.commit()
        
        # Enviar email de confirmação com link
        send_trial_confirmation_email_with_link(trial)
        
        flash(f'Aula experimental agendada para {scheduled_date_str} às {scheduled_time_str}!', 'success')
        return redirect(url_for('trial_lessons.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao agendar aula: {str(e)}', 'error')
        return redirect(url_for('trial_lessons.view', id=id))


@bp.route('/<int:id>/reschedule', methods=['POST'])
@admin_or_secretary_required
def reschedule(id):
    """Reagendar uma aula experimental"""
    trial = TrialLesson.query.get_or_404(id)
    
    try:
        scheduled_date_str = request.form.get('scheduled_date')
        scheduled_time_str = request.form.get('scheduled_time')
        
        if not all([scheduled_date_str, scheduled_time_str]):
            flash('Preencha data e hora.', 'error')
            return redirect(url_for('trial_lessons.view', id=id))
        
        scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M').time()
        
        trial.scheduled_date = scheduled_date
        trial.scheduled_time = scheduled_time
        trial.notes = request.form.get('notes', trial.notes)
        
        db.session.commit()
        
        # Enviar email de reagendamento
        send_trial_reschedule_email(trial)
        
        flash('Aula experimental reagendada com sucesso!', 'success')
        return redirect(url_for('trial_lessons.view', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reagendar: {str(e)}', 'error')
        return redirect(url_for('trial_lessons.view', id=id))


@bp.route('/<int:id>/complete', methods=['POST'])
@admin_or_secretary_required
def complete(id):
    """Marcar aula como concluída"""
    trial = TrialLesson.query.get_or_404(id)
    
    trial.status = 'completed'
    trial.notes = request.form.get('notes', trial.notes)
    
    db.session.commit()
    
    flash('Aula experimental marcada como concluída!', 'success')
    return redirect(url_for('trial_lessons.index'))


@bp.route('/<int:id>/cancel', methods=['POST'])
@admin_or_secretary_required
def cancel(id):
    """Cancelar uma aula experimental"""
    trial = TrialLesson.query.get_or_404(id)
    
    cancellation_reason = request.form.get('cancellation_reason', '')
    
    trial.status = 'cancelled'
    trial.notes = f"Cancelado: {cancellation_reason}\n{trial.notes or ''}"
    
    db.session.commit()
    
    # Enviar email de cancelamento
    send_trial_cancellation_email(trial, cancellation_reason)
    
    flash('Aula experimental cancelada.', 'info')
    return redirect(url_for('trial_lessons.index'))


@bp.route('/<int:id>/send-confirmation', methods=['POST'])
@admin_or_secretary_required
def send_confirmation(id):
    """Reenviar email de confirmação"""
    trial = TrialLesson.query.get_or_404(id)
    
    if trial.status != 'scheduled':
        flash('Apenas aulas agendadas podem receber email de confirmação.', 'error')
        return redirect(url_for('trial_lessons.view', id=id))
    
    send_trial_confirmation_email(trial)
    
    flash('Email de confirmação enviado!', 'success')
    return redirect(url_for('trial_lessons.view', id=id))


@bp.route('/<int:id>/delete', methods=['POST'])
@admin_or_secretary_required
def delete(id):
    """Deletar uma solicitação"""
    trial = TrialLesson.query.get_or_404(id)
    
    if current_user.role != 'admin':
        flash('Apenas administradores podem deletar solicitações.', 'error')
        return redirect(url_for('trial_lessons.index'))
    
    db.session.delete(trial)
    db.session.commit()
    
    flash('Solicitação deletada.', 'info')
    return redirect(url_for('trial_lessons.index'))


# ============================================================================
# ROTAS PÚBLICAS PARA CONFIRMAÇÃO DO USUÁRIO
# ============================================================================

@bp.route('/confirm/<token>')
def user_confirm(token):
    """Rota pública para usuário confirmar presença"""
    trial = TrialLesson.query.filter_by(confirmation_token=token).first_or_404()
    
    if trial.user_confirmed:
        return render_template('trial_lessons/already_confirmed.html', trial=trial)
    
    if trial.user_declined:
        return render_template('trial_lessons/already_declined.html', trial=trial)
    
    if trial.status != 'scheduled':
        flash('Esta aula não está mais disponível para confirmação.', 'error')
        return redirect(url_for('public.index'))
    
    return render_template('trial_lessons/confirm.html', trial=trial, token=token)


@bp.route('/confirm/<token>/accept', methods=['POST'])
def user_confirm_accept(token):
    """Usuário confirma presença"""
    trial = TrialLesson.query.filter_by(confirmation_token=token).first_or_404()
    
    if trial.user_confirmed:
        flash('Você já confirmou presença para esta aula.', 'info')
        return redirect(url_for('trial_lessons.user_confirm', token=token))
    
    trial.user_confirmed = True
    trial.user_confirmed_at = datetime.utcnow()
    db.session.commit()
    
    # Enviar email de agradecimento
    send_user_confirmation_thank_you_email(trial)
    
    # Notificar admin
    send_user_confirmation_notification_to_admin(trial, confirmed=True)
    
    return render_template('trial_lessons/confirmed_success.html', trial=trial)


@bp.route('/confirm/<token>/decline', methods=['POST'])
def user_confirm_decline(token):
    """Usuário recusa o agendamento"""
    trial = TrialLesson.query.filter_by(confirmation_token=token).first_or_404()
    
    if trial.user_declined:
        flash('Você já recusou esta aula.', 'info')
        return redirect(url_for('trial_lessons.user_confirm', token=token))
    
    reason = request.form.get('decline_reason', 'Não informado')
    
    trial.user_declined = True
    trial.user_declined_at = datetime.utcnow()
    trial.notes = f"{trial.notes or ''}\n\nUsuário recusou: {reason}"
    trial.status = 'cancelled'
    db.session.commit()
    
    # Notificar admin sobre recusa
    send_user_confirmation_notification_to_admin(trial, confirmed=False, reason=reason)
    
    return render_template('trial_lessons/declined_success.html', trial=trial)


# ============================================================================
# FUNÇÕES DE ENVIO DE EMAIL
# ============================================================================

def send_trial_confirmation_email(trial):
    """Enviar email de confirmação de agendamento"""
    try:
        teacher_name = trial.assigned_teacher.user.full_name if trial.assigned_teacher else 'A definir'
        room_name = trial.room.name if trial.room else 'A definir'
        
        date_formatted = trial.scheduled_date.strftime('%d/%m/%Y')
        time_formatted = trial.scheduled_time.strftime('%H:%M')
        
        subject = f'✅ Aula Experimental Confirmada - {trial.instrument}'
        
        message = f"""Olá {trial.full_name},

Sua aula experimental foi CONFIRMADA! 🎉

📋 DETALHES DO AGENDAMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Instrumento: {trial.instrument}
📅 Data: {date_formatted}
⏰ Horário: {time_formatted}
⏱️ Duração: {trial.duration_minutes} minutos
👨‍🏫 Professor(a): {teacher_name}
📍 Sala: {room_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 INFORMAÇÕES IMPORTANTES:

• Chegue com 10 minutos de antecedência
• Traga seu instrumento (se tiver)
• Se precisar remarcar, entre em contato com até 24h de antecedência

📞 Contato: {trial.phone}
📧 Email: {trial.email}

Estamos ansiosos para conhecê-lo(a)!

Atenciosamente,
Escola de Música Sol Maior
"""
        
        success = send_email(trial.email, subject, message)
        
        if success:
            trial.confirmation_sent = True
            db.session.commit()
            
        return success
        
    except Exception as e:
        print(f'Erro ao enviar email de confirmação: {str(e)}')
        return False


def send_trial_reschedule_email(trial):
    """Enviar email de reagendamento"""
    try:
        date_formatted = trial.scheduled_date.strftime('%d/%m/%Y')
        time_formatted = trial.scheduled_time.strftime('%H:%M')
        
        subject = f'📅 Aula Experimental Reagendada - {trial.instrument}'
        
        message = f"""Olá {trial.full_name},

Sua aula experimental foi REAGENDADA.

📋 NOVA DATA E HORÁRIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Instrumento: {trial.instrument}
📅 Nova Data: {date_formatted}
⏰ Novo Horário: {time_formatted}
⏱️ Duração: {trial.duration_minutes} minutos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se tiver alguma dúvida, entre em contato conosco.

Atenciosamente,
Escola de Música Sol Maior
"""
        
        return send_email(trial.email, subject, message)
        
    except Exception as e:
        print(f'Erro ao enviar email de reagendamento: {str(e)}')
        return False


def send_trial_cancellation_email(trial, reason):
    """Enviar email de cancelamento"""
    try:
        subject = f'❌ Aula Experimental Cancelada - {trial.instrument}'
        
        message = f"""Olá {trial.full_name},

Informamos que sua aula experimental foi cancelada.

Motivo: {reason if reason else 'Não especificado'}

Se desejar reagendar, entre em contato conosco.

Atenciosamente,
Escola de Música Sol Maior
"""
        
        return send_email(trial.email, subject, message)
        
    except Exception as e:
        print(f'Erro ao enviar email de cancelamento: {str(e)}')
        return False


def send_trial_confirmation_email_with_link(trial):
    """Enviar email de confirmação com link para aceitar/recusar"""
    try:
        teacher_name = trial.assigned_teacher.user.full_name if trial.assigned_teacher else 'A definir'
        room_name = trial.room.name if trial.room else 'A definir'
        
        date_formatted = trial.scheduled_date.strftime('%d/%m/%Y')
        time_formatted = trial.scheduled_time.strftime('%H:%M')
        
        # URL base (deve ser configurada em produção)
        base_url = request.host_url.rstrip('/')
        confirm_url = f"{base_url}/trial-lessons/confirm/{trial.confirmation_token}"
        
        subject = f'✅ Aula Experimental Confirmada - {trial.instrument}'
        
        message = f"""Olá {trial.full_name},

Sua aula experimental foi CONFIRMADA! 🎉

📋 DETALHES DO AGENDAMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Instrumento: {trial.instrument}
📅 Data: {date_formatted}
⏰ Horário: {time_formatted}
⏱️ Duração: {trial.duration_minutes} minutos
👨‍🏫 Professor(a): {teacher_name}
📍 Sala: {room_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ CONFIRME SUA PRESENÇA:

Por favor, confirme sua presença acessando o link abaixo:

🔗 {confirm_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 INFORMAÇÕES IMPORTANTES:

• Chegue com 10 minutos de antecedência
• Traga seu instrumento (se tiver)
• Se precisar remarcar, entre em contato com até 24h de antecedência
• Caso não possa comparecer, use o link acima para cancelar

📞 Contato: {trial.phone}
📧 Email: {trial.email}

Estamos ansiosos para conhecê-lo(a)!

Atenciosamente,
Escola de Música Sol Maior
"""
        
        success = send_email(trial.email, subject, message)
        
        if success:
            trial.confirmation_sent = True
            db.session.commit()
            
        return success
        
    except Exception as e:
        print(f'Erro ao enviar email de confirmação: {str(e)}')
        return False


def send_user_confirmation_thank_you_email(trial):
    """Email de agradecimento após confirmação do usuário"""
    try:
        date_formatted = trial.scheduled_date.strftime('%d/%m/%Y')
        time_formatted = trial.scheduled_time.strftime('%H:%M')
        
        subject = f'🎉 Presença Confirmada - Aula Experimental'
        
        message = f"""Olá {trial.full_name},

Obrigado por confirmar sua presença! 🎉

📋 LEMBRETE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Instrumento: {trial.instrument}
📅 Data: {date_formatted}
⏰ Horário: {time_formatted}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sua presença foi confirmada com sucesso!
Nos vemos em breve.

✅ Você receberá um lembrete 1 dia antes da aula.

Atenciosamente,
Escola de Música Sol Maior
"""
        
        return send_email(trial.email, subject, message)
        
    except Exception as e:
        print(f'Erro ao enviar email de agradecimento: {str(e)}')
        return False


def send_user_confirmation_notification_to_admin(trial, confirmed=True, reason=None):
    """Notificar admin sobre confirmação/recusa do usuário"""
    try:
        from app.models import User
        
        # Buscar admin e secretaria
        admins = User.query.filter(User.role.in_(['admin', 'secretary']), User.is_active == True).all()
        
        if confirmed:
            subject = f'✅ Usuário Confirmou Presença - Aula Experimental'
            action = "CONFIRMOU"
            emoji = "✅"
        else:
            subject = f'❌ Usuário Recusou Agendamento - Aula Experimental'
            action = "RECUSOU"
            emoji = "❌"
        
        date_formatted = trial.scheduled_date.strftime('%d/%m/%Y')
        time_formatted = trial.scheduled_time.strftime('%H:%M')
        
        message = f"""{emoji} Atualização de Aula Experimental

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 {trial.full_name} {action} a aula experimental

📋 Detalhes:
• Instrumento: {trial.instrument}
• Data: {date_formatted} às {time_formatted}
• Email: {trial.email}
• Telefone: {trial.phone}

{f'Motivo da recusa: {reason}' if not confirmed and reason else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Acesse: http://localhost:5000/trial-lessons/{trial.id}
"""
        
        # Enviar para todos admins/secretaria
        for admin in admins:
            send_email(admin.email, subject, message)
        
        return True
        
    except Exception as e:
        print(f'Erro ao enviar notificação: {str(e)}')
        return False
