"""
Sistema de Tarefas Automatizadas
- Lembretes de aula (24h antes)
- Marcação automática de faltas
- Envio de emails de confirmação
- Processamento de notificações agendadas
"""

from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Mail, Message
from app import db
from app.models import (LessonSchedule, ScheduledNotification, Student, Teacher, 
                        Payment, MakeupLesson, User)
from sqlalchemy import and_, or_, func
import logging

logger = logging.getLogger(__name__)

mail = Mail()


def init_mail(app):
    """Inicializar Flask-Mail com a aplicação"""
    mail.init_app(app)


def send_email(recipient_email, subject, body):
    """Enviar email usando Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f'Erro ao enviar email para {recipient_email}: {str(e)}')
        return False


def create_lesson_reminders():
    """
    Criar lembretes de aula para as próximas 24 horas
    Deve ser executado diariamente
    """
    try:
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Buscar todas as aulas agendadas para amanhã
        lessons = LessonSchedule.query.filter(
            LessonSchedule.lesson_date == tomorrow,
            LessonSchedule.status == 'scheduled'
        ).all()
        
        for lesson in lessons:
            # Verificar se já existe lembrete criado
            existing = ScheduledNotification.query.filter(
                ScheduledNotification.notification_type == 'lesson_reminder',
                ScheduledNotification.related_lesson_id == lesson.id,
                ScheduledNotification.status.in_(['pending', 'sent'])
            ).first()
            
            if existing:
                continue
            
            # Criar lembrete para o aluno
            student_notification = ScheduledNotification(
                notification_type='lesson_reminder',
                recipient_id=lesson.student.user_id,
                recipient_email=lesson.student.user.email,
                subject='Lembrete: Você tem aula amanhã!',
                message=f'Olá {lesson.student.user.full_name},\n\n'
                       f'Este é um lembrete de que você tem aula de {lesson.student.instrument} amanhã:\n\n'
                       f'📅 Data: {lesson.lesson_date.strftime("%d/%m/%Y")}\n'
                       f'⏰ Horário: {lesson.start_time.strftime("%H:%M")}\n'
                       f'👨‍🏫 Professor(a): {lesson.teacher.user.full_name}\n'
                       f'📍 Sala: {lesson.room.name if lesson.room else "A definir"}\n\n'
                       f'Nos vemos em breve!\n\n'
                       f'Atenciosamente,\nEscola de Música Solmaior',
                related_lesson_id=lesson.id,
                scheduled_for=datetime.now() + timedelta(hours=1),
                status='pending'
            )
            db.session.add(student_notification)
            
            # Criar lembrete para o professor
            teacher_notification = ScheduledNotification(
                notification_type='lesson_reminder',
                recipient_id=lesson.teacher.user_id,
                recipient_email=lesson.teacher.user.email,
                subject='Lembrete: Aula agendada para amanhã',
                message=f'Olá {lesson.teacher.user.full_name},\n\n'
                       f'Lembrete de aula agendada para amanhã:\n\n'
                       f'👨‍🎓 Aluno: {lesson.student.user.full_name}\n'
                       f'🎵 Instrumento: {lesson.student.instrument}\n'
                       f'📅 Data: {lesson.lesson_date.strftime("%d/%m/%Y")}\n'
                       f'⏰ Horário: {lesson.start_time.strftime("%H:%M")}\n'
                       f'📍 Sala: {lesson.room.name if lesson.room else "A definir"}\n\n'
                       f'Atenciosamente,\nEscola de Música Solmaior',
                related_lesson_id=lesson.id,
                scheduled_for=datetime.now() + timedelta(hours=1),
                status='pending'
            )
            db.session.add(teacher_notification)
        
        db.session.commit()
        logger.info(f'Criados lembretes para {len(lessons)} aulas')
        return len(lessons)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao criar lembretes de aula: {str(e)}')
        return 0


def mark_automatic_absences():
    """
    Marcar automaticamente como falta aulas não confirmadas
    Deve ser executado diariamente para aulas do dia anterior
    """
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        
        # Buscar aulas não confirmadas de ontem
        unconfirmed_lessons = LessonSchedule.query.filter(
            LessonSchedule.lesson_date == yesterday,
            LessonSchedule.status == 'scheduled',
            LessonSchedule.attendance_confirmed == False
        ).all()
        
        for lesson in unconfirmed_lessons:
            lesson.status = 'absent'
            lesson.attendance_status = 'absent'
            lesson.attendance_confirmed = True
            lesson.confirmed_at = datetime.utcnow()
            
            # Criar notificação de falta
            notification = ScheduledNotification(
                notification_type='auto_absence',
                recipient_id=lesson.student.user_id,
                recipient_email=lesson.student.user.email,
                subject='Falta registrada automaticamente',
                message=f'Olá {lesson.student.user.full_name},\n\n'
                       f'Foi registrada uma falta na sua aula do dia {lesson.lesson_date.strftime("%d/%m/%Y")} '
                       f'às {lesson.start_time.strftime("%H:%M")}.\n\n'
                       f'Se você compareceu à aula ou tem uma justificativa, '
                       f'por favor entre em contato com a secretaria.\n\n'
                       f'Atenciosamente,\nEscola de Música Solmaior',
                related_lesson_id=lesson.id,
                scheduled_for=datetime.utcnow(),
                status='pending'
            )
            db.session.add(notification)
        
        db.session.commit()
        logger.info(f'Marcadas {len(unconfirmed_lessons)} faltas automáticas')
        return len(unconfirmed_lessons)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao marcar faltas automáticas: {str(e)}')
        return 0


def send_payment_reminders():
    """
    Enviar lembretes de pagamentos pendentes
    - 3 dias antes do vencimento
    - No dia do vencimento
    - 3 dias após o vencimento
    """
    try:
        today = datetime.now().date()
        
        # Pagamentos vencendo em 3 dias
        upcoming_payments = Payment.query.filter(
            Payment.status == 'pending',
            Payment.due_date == today + timedelta(days=3)
        ).all()
        
        for payment in upcoming_payments:
            create_payment_reminder(payment, 'upcoming')
        
        # Pagamentos vencendo hoje
        due_today = Payment.query.filter(
            Payment.status == 'pending',
            Payment.due_date == today
        ).all()
        
        for payment in due_today:
            create_payment_reminder(payment, 'due_today')
        
        # Pagamentos vencidos há 3 dias
        overdue = Payment.query.filter(
            Payment.status == 'pending',
            Payment.due_date == today - timedelta(days=3)
        ).all()
        
        for payment in overdue:
            create_payment_reminder(payment, 'overdue')
        
        db.session.commit()
        total = len(upcoming_payments) + len(due_today) + len(overdue)
        logger.info(f'Criados {total} lembretes de pagamento')
        return total
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao criar lembretes de pagamento: {str(e)}')
        return 0


def create_payment_reminder(payment, reminder_type):
    """Criar lembrete de pagamento específico"""
    student = payment.enrollment.student
    
    # Verificar se já existe lembrete similar
    existing = ScheduledNotification.query.filter(
        ScheduledNotification.notification_type == f'payment_{reminder_type}',
        ScheduledNotification.related_payment_id == payment.id,
        ScheduledNotification.status.in_(['pending', 'sent']),
        func.date(ScheduledNotification.scheduled_for) == datetime.now().date()
    ).first()
    
    if existing:
        return
    
    if reminder_type == 'upcoming':
        subject = 'Lembrete: Pagamento vence em 3 dias'
        message = f'Olá {student.user.full_name},\n\n' \
                 f'Seu pagamento referente a {payment.reference_month.strftime("%m/%Y")} ' \
                 f'vence em 3 dias.\n\n' \
                 f'💰 Valor: R$ {payment.total_amount:.2f}\n' \
                 f'📅 Vencimento: {payment.due_date.strftime("%d/%m/%Y")}\n\n' \
                 f'Atenciosamente,\nEscola de Música Solmaior'
    
    elif reminder_type == 'due_today':
        subject = 'Lembrete: Pagamento vence hoje'
        message = f'Olá {student.user.full_name},\n\n' \
                 f'Seu pagamento referente a {payment.reference_month.strftime("%m/%Y")} ' \
                 f'vence hoje.\n\n' \
                 f'💰 Valor: R$ {payment.total_amount:.2f}\n' \
                 f'📅 Vencimento: {payment.due_date.strftime("%d/%m/%Y")}\n\n' \
                 f'Atenciosamente,\nEscola de Música Solmaior'
    
    else:  # overdue
        subject = 'Aviso: Pagamento em atraso'
        message = f'Olá {student.user.full_name},\n\n' \
                 f'Identificamos que seu pagamento referente a {payment.reference_month.strftime("%m/%Y")} ' \
                 f'está em atraso.\n\n' \
                 f'💰 Valor original: R$ {payment.amount:.2f}\n' \
                 f'📅 Vencimento: {payment.due_date.strftime("%d/%m/%Y")}\n\n' \
                 f'Por favor, regularize sua situação o quanto antes para evitar multas adicionais.\n\n' \
                 f'Atenciosamente,\nEscola de Música Solmaior'
    
    notification = ScheduledNotification(
        notification_type=f'payment_{reminder_type}',
        recipient_id=student.user_id,
        recipient_email=student.user.email,
        subject=subject,
        message=message,
        related_payment_id=payment.id,
        scheduled_for=datetime.utcnow(),
        status='pending'
    )
    db.session.add(notification)


def process_pending_notifications():
    """
    Processar e enviar notificações pendentes
    Deve ser executado a cada hora
    """
    try:
        # Buscar notificações pendentes que devem ser enviadas
        pending_notifications = ScheduledNotification.query.filter(
            ScheduledNotification.status == 'pending',
            ScheduledNotification.scheduled_for <= datetime.utcnow()
        ).limit(100).all()

        sent_count = 0
        failed_count = 0

        for notification in pending_notifications:
            try:
                success = False

                # Enviar por email se configurado
                if notification.recipient_email:
                    success = send_email(
                        notification.recipient_email,
                        notification.subject,
                        notification.message
                    )

                # TODO: Implementar envio por SMS e push notification
                # if notification.recipient_phone:
                #     send_sms(notification.recipient_phone, notification.message)

                if success:
                    notification.status = 'sent'
                    notification.sent_at = datetime.utcnow()
                    sent_count += 1
                else:
                    notification.status = 'failed'
                    notification.error_message = 'Falha ao enviar notificação'
                    notification.retry_count += 1
                    failed_count += 1

                    # Reagendar se não excedeu limite de tentativas
                    if notification.retry_count < 3:
                        notification.status = 'pending'
                        notification.scheduled_for = datetime.utcnow() + timedelta(hours=1)

            except Exception as e:
                notification.status = 'failed'
                notification.error_message = str(e)
                notification.retry_count += 1
                failed_count += 1
                logger.error(f'Erro ao processar notificação {notification.id}: {str(e)}')

        db.session.commit()
        logger.info(f'Processadas {len(pending_notifications)} notificações: '
                   f'{sent_count} enviadas, {failed_count} falharam')

        return {'sent': sent_count, 'failed': failed_count}

    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao processar notificações: {str(e)}')
        return {'sent': 0, 'failed': 0}


def send_bulk_notifications():
    """
    Enviar notificações em lote para campanhas
    """
    try:
        # Exemplo: lembretes de pagamento para todos os alunos com pagamentos pendentes
        pending_payments = Payment.query.filter_by(status='pending').all()

        notifications_created = 0
        for payment in pending_payments:
            student = payment.enrollment.student

            # Verificar se já existe lembrete hoje
            existing = ScheduledNotification.query.filter(
                ScheduledNotification.recipient_id == student.user_id,
                ScheduledNotification.notification_type == 'payment_reminder_bulk',
                func.date(ScheduledNotification.scheduled_for) == datetime.now().date()
            ).first()

            if not existing:
                notification = ScheduledNotification(
                    notification_type='payment_reminder_bulk',
                    recipient_id=student.user_id,
                    recipient_email=student.user.email,
                    subject='Lembrete: Você tem pagamentos pendentes',
                    message=f'Olá {student.user.full_name},\n\n'
                           f'Identificamos que você possui pagamentos pendentes.\n'
                           f'Acesse o sistema para visualizar e regularizar.\n\n'
                           f'Atenciosamente,\nEscola de Música Solmaior',
                    scheduled_for=datetime.utcnow() + timedelta(hours=2),  # Enviar em 2 horas
                    status='pending'
                )
                db.session.add(notification)
                notifications_created += 1

        db.session.commit()
        logger.info(f'Criadas {notifications_created} notificações em lote')
        return notifications_created

    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao enviar notificações em lote: {str(e)}')
        return 0


def run_daily_tasks():
    """
    Executar todas as tarefas diárias
    Deve ser agendado para rodar uma vez por dia (ex: 8h da manhã)
    """
    logger.info('Iniciando tarefas diárias...')

    results = {
        'lesson_reminders': create_lesson_reminders(),
        'automatic_absences': mark_automatic_absences(),
        'payment_reminders': send_payment_reminders(),
        'consistency_checks': run_consistency_checks(),
        'predictive_updates': update_predictive_indicators()
    }

    logger.info(f'Tarefas diárias concluídas: {results}')
    return results


def run_consistency_checks():
    """Executar verificações de consistência diárias"""
    try:
        from app.services import EnrollmentService

        # Verificar consistência Enrollment ↔ Student.is_active
        issues_fixed = EnrollmentService.check_and_fix_consistency()
        logger.info(f'Verificações de consistência: {issues_fixed} problemas corrigidos')
        return issues_fixed
    except Exception as e:
        logger.error(f'Erro nas verificações de consistência: {str(e)}')
        return 0


def update_predictive_indicators():
    """Atualizar indicadores preditivos"""
    try:
        from app.services import PredictiveService

        results = PredictiveService.update_all_predictive_indicators()
        logger.info(f'Indicadores preditivos atualizados: {results}')
        return results
    except Exception as e:
        logger.error(f'Erro ao atualizar indicadores preditivos: {str(e)}')
        return {}


def run_hourly_tasks():
    """
    Executar tarefas que devem rodar a cada hora
    """
    logger.info('Iniciando tarefas horárias...')
    
    results = {
        'notifications_sent': process_pending_notifications()
    }
    
    logger.info(f'Tarefas horárias concluídas: {results}')
    return results
