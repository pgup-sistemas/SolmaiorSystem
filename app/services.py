# ============================================================================
# SERVICES LAYER - Lógica de Negócio
# ============================================================================

from datetime import datetime, timedelta
from app import db
from app.models import (
    LessonSchedule, LessonWaitlist, MakeupLessonSuggestion,
    InstrumentLessonPolicy, StudentLessonCredit, FrequencyDiscount,
    FinancialAuditLog, NotificationPreference, PredictiveIndicator,
    Student, Teacher, Room, Billing, Discount
)


class ScheduleService:
    """Serviço de gestão de agenda"""

    @staticmethod
    def validate_lesson_conflict(teacher_id, student_id, room_id, start_time, end_time):
        """Valida conflitos de professor, aluno e sala"""
        
        # Conflito de professor
        teacher_conflict = LessonSchedule.query.filter(
            LessonSchedule.teacher_id == teacher_id,
            LessonSchedule.start_time < end_time,
            LessonSchedule.end_time > start_time,
            LessonSchedule.status != 'cancelada'
        ).first()
        
        if teacher_conflict:
            return False, "Professor já tem aula neste horário"
        
        # Conflito de aluno
        student_conflict = LessonSchedule.query.filter(
            LessonSchedule.student_id == student_id,
            LessonSchedule.start_time < end_time,
            LessonSchedule.end_time > start_time,
            LessonSchedule.status != 'cancelada'
        ).first()
        
        if student_conflict:
            return False, "Aluno já tem aula neste horário"
        
        # Conflito de sala
        room_conflict = LessonSchedule.query.filter(
            LessonSchedule.room_id == room_id,
            LessonSchedule.start_time < end_time,
            LessonSchedule.end_time > start_time,
            LessonSchedule.status != 'cancelada'
        ).first()
        
        if room_conflict:
            return False, "Sala já está ocupada neste horário"
        
        return True, "OK"

    @staticmethod
    def check_weekly_limit(student_id, duration, week_start):
        """Verifica se aluno não excede limite semanal"""
        week_end = week_start + timedelta(days=7)
        
        # Buscar política do instrumento
        student = Student.query.get(student_id)
        policy = InstrumentLessonPolicy.query.filter_by(
            instrument=student.instrument,
            is_active=True
        ).first()
        
        max_minutes = policy.max_weekly_minutes if policy else 60
        
        total_minutes = db.session.query(
            db.func.sum(LessonSchedule.duration)
        ).filter(
            LessonSchedule.student_id == student_id,
            LessonSchedule.start_time >= week_start,
            LessonSchedule.start_time < week_end,
            LessonSchedule.status != 'cancelada'
        ).scalar() or 0
        
        if total_minutes + duration > max_minutes:
            return False, f"Aluno já tem {total_minutes} minutos. Limite: {max_minutes} minutos/semana"
        
        return True, "OK"


class WaitlistService:
    """Serviço de fila de espera"""

    @staticmethod
    def add_to_waitlist(student_id, teacher_id, instrument, preferred_day, preferred_time, duration):
        """Adiciona aluno à fila de espera"""
        
        # Contar quantos já estão na fila (para prioridade)
        priority = LessonWaitlist.query.filter_by(
            status='waiting'
        ).count()
        
        waitlist_entry = LessonWaitlist(
            student_id=student_id,
            teacher_id=teacher_id,
            instrument=instrument,
            preferred_day=preferred_day,
            preferred_time=preferred_time,
            duration=duration,
            priority=priority,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(waitlist_entry)
        db.session.commit()
        return waitlist_entry

    @staticmethod
    def check_and_notify_waitlist():
        """Verifica fila de espera e notifica quando horário fica disponível"""
        
        waiting_entries = LessonWaitlist.query.filter_by(status='waiting').all()
        
        for entry in waiting_entries:
            # Verificar se horário está disponível
            is_available, _ = ScheduleService.validate_lesson_conflict(
                entry.teacher_id,
                entry.student_id,
                None,  # Qualquer sala
                datetime.utcnow(),
                datetime.utcnow() + timedelta(hours=1)
            )
            
            if is_available:
                entry.status = 'matched'
                entry.matched_at = datetime.utcnow()
                db.session.commit()
                # TODO: Enviar notificação por email


class MakeupLessonService:
    """Serviço de reposição inteligente"""

    @staticmethod
    def create_makeup_suggestions(original_lesson_id):
        """Cria sugestões automáticas de reposição"""
        
        original_lesson = LessonSchedule.query.get(original_lesson_id)
        if not original_lesson:
            return None
        
        # Buscar 3 melhores horários nos próximos 30 dias
        suggested_slots = []
        
        for i in range(1, 31):
            check_date = datetime.utcnow() + timedelta(days=i)
            
            # Verificar disponibilidade do professor
            is_available, _ = ScheduleService.validate_lesson_conflict(
                original_lesson.teacher_id,
                original_lesson.student_id,
                original_lesson.room_id,
                check_date,
                check_date + timedelta(minutes=original_lesson.duration)
            )
            
            if is_available:
                suggested_slots.append({
                    'date': check_date.isoformat(),
                    'time': check_date.strftime('%H:%M')
                })
            
            if len(suggested_slots) >= 3:
                break
        
        suggestion = MakeupLessonSuggestion(
            original_lesson_id=original_lesson_id,
            student_id=original_lesson.student_id,
            teacher_id=original_lesson.teacher_id,
            suggested_slots=suggested_slots,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(suggestion)
        db.session.commit()
        return suggestion


class FinancialService:
    """Serviço de gestão financeira"""

    @staticmethod
    def calculate_frequency_discount(student_id, month, year):
        """Calcula desconto por frequência"""
        
        # Contar aulas do mês
        total_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student_id,
            db.extract('month', LessonSchedule.start_time) == month,
            db.extract('year', LessonSchedule.start_time) == year,
            LessonSchedule.status.in_(['realizada', 'falta'])
        ).count()
        
        # Contar faltas
        absences = LessonSchedule.query.filter(
            LessonSchedule.student_id == student_id,
            db.extract('month', LessonSchedule.start_time) == month,
            db.extract('year', LessonSchedule.start_time) == year,
            LessonSchedule.status == 'falta'
        ).count()
        
        if total_lessons == 0:
            attendance_rate = 0
            discount_percentage = 0
        else:
            attendance_rate = ((total_lessons - absences) / total_lessons) * 100
            
            # Tabela de descontos
            if attendance_rate >= 100:
                discount_percentage = 10
            elif attendance_rate >= 90:
                discount_percentage = 5
            elif attendance_rate >= 80:
                discount_percentage = 2
            else:
                discount_percentage = 0
        
        # Criar registro de desconto
        freq_discount = FrequencyDiscount(
            student_id=student_id,
            month=month,
            year=year,
            attendance_rate=attendance_rate,
            discount_percentage=discount_percentage,
            reason=f"Frequência {attendance_rate:.1f}%"
        )
        
        db.session.add(freq_discount)
        db.session.commit()
        return freq_discount

    @staticmethod
    def log_financial_action(user_id, action, entity_type, entity_id, old_value, new_value, reason, ip_address, user_agent):
        """Registra ação financeira na auditoria"""
        
        audit_log = FinancialAuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        return audit_log


class NotificationService:
    """Serviço de notificações inteligentes"""

    @staticmethod
    def should_send_notification(user_id, notification_type):
        """Verifica se deve enviar notificação baseado em preferências"""
        
        pref = NotificationPreference.query.filter_by(
            user_id=user_id,
            notification_type=notification_type
        ).first()
        
        if not pref or not pref.enabled:
            return False
        
        # Verificar horários silenciosos
        if pref.quiet_hours_start and pref.quiet_hours_end:
            now = datetime.utcnow().time()
            if pref.quiet_hours_start <= now <= pref.quiet_hours_end:
                return False
        
        return True

    @staticmethod
    def get_notification_priority(notification_type):
        """Retorna prioridade da notificação"""
        
        priorities = {
            'lesson_reminder': 'high',
            'payment_due': 'high',
            'lesson_cancelled': 'medium',
            'recital_confirmed': 'medium',
            'news': 'low'
        }
        
        return priorities.get(notification_type, 'medium')


def generate_simple_receipt(payment):
    """Gera recibo simples em texto para download"""
    from io import BytesIO
    
    buffer = BytesIO()
    
    # Gerar recibo em texto simples
    receipt_text = f"""
═══════════════════════════════════════════════════════════════
           ESCOLA DE MÚSICA SOL MAIOR
           RECIBO DE PAGAMENTO
═══════════════════════════════════════════════════════════════

Recibo Nº: {payment.receipt_number or f'REC-{payment.id:05d}'}
Data de Pagamento: {payment.payment_date.strftime('%d/%m/%Y')}

───────────────────────────────────────────────────────────────
DADOS DO ALUNO
───────────────────────────────────────────────────────────────
Nome: {payment.enrollment.student.user.full_name}
Referência: {payment.reference_month.strftime('%m/%Y') if payment.reference_month else 'N/A'}

───────────────────────────────────────────────────────────────
VALORES
───────────────────────────────────────────────────────────────
Valor da Mensalidade:        R$ {payment.amount:.2f}
Desconto:                   -R$ {payment.discount:.2f}
Multa/Juros:                +R$ {payment.late_fee:.2f}
                             ─────────────
TOTAL PAGO:                  R$ {payment.total_amount:.2f}

───────────────────────────────────────────────────────────────
Forma de Pagamento: {payment.payment_method or 'Não especificado'}

{f'Observações: {payment.notes}' if payment.notes else ''}

───────────────────────────────────────────────────────────────
                    
Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

═══════════════════════════════════════════════════════════════
           Sol Maior - Escola de Música
           www.solmaior.com.br
═══════════════════════════════════════════════════════════════
"""
    
    buffer.write(receipt_text.encode('utf-8'))
    buffer.seek(0)
    
    return buffer


class PredictiveService:
    """Serviço de indicadores preditivos"""

    @staticmethod
    def calculate_churn_risk(student_id):
        """Calcula risco de evasão do aluno"""
        
        student = Student.query.get(student_id)
        if not student:
            return None
        
        risk_score = 0
        reasons = []
        
        # Verificar 2+ faltas consecutivas
        recent_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student_id,
            LessonSchedule.start_time >= datetime.utcnow() - timedelta(days=30)
        ).order_by(LessonSchedule.start_time.desc()).limit(3).all()
        
        consecutive_absences = sum(1 for l in recent_lessons if l.status == 'falta')
        if consecutive_absences >= 2:
            risk_score += 30
            reasons.append("2+ faltas consecutivas")
        
        # Verificar atraso em pagamento
        overdue_billing = Billing.query.filter(
            Billing.student_id == student_id,
            Billing.status == 'overdue',
            Billing.due_date < datetime.utcnow().date()
        ).first()
        
        if overdue_billing:
            risk_score += 25
            reasons.append("Pagamento em atraso")
        
        # Verificar sem aula há 30 dias
        last_lesson = LessonSchedule.query.filter(
            LessonSchedule.student_id == student_id,
            LessonSchedule.status.in_(['realizada', 'falta'])
        ).order_by(LessonSchedule.start_time.desc()).first()
        
        if not last_lesson or (datetime.utcnow() - last_lesson.start_time).days > 30:
            risk_score += 20
            reasons.append("Sem aula há 30 dias")
        
        # Criar indicador
        indicator = PredictiveIndicator(
            indicator_type='churn_risk',
            entity_type='Student',
            entity_id=student_id,
            value=min(risk_score, 100),
            description="; ".join(reasons) if reasons else "Sem risco detectado",
            action_required=risk_score > 50,
            action_description="Contatar aluno para acompanhamento" if risk_score > 50 else None
        )
        
        db.session.add(indicator)
        db.session.commit()
        return indicator

    @staticmethod
    def calculate_revenue_forecast(days_ahead=30):
        """Calcula previsão de receita"""
        
        forecast_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        # Somar cobranças esperadas
        expected_revenue = db.session.query(
            db.func.sum(Billing.amount)
        ).filter(
            Billing.status.in_(['pending', 'overdue']),
            Billing.due_date <= forecast_date.date()
        ).scalar() or 0
        
        # Somar cobranças em risco
        at_risk_revenue = db.session.query(
            db.func.sum(Billing.amount)
        ).filter(
            Billing.status == 'overdue'
        ).scalar() or 0
        
        indicator = PredictiveIndicator(
            indicator_type='revenue_forecast',
            entity_type='School',
            entity_id=None,
            value=expected_revenue,
            description=f"Receita esperada: R$ {expected_revenue:.2f}. Em risco: R$ {at_risk_revenue:.2f}",
            action_required=at_risk_revenue > 0
        )
        
        db.session.add(indicator)
        db.session.commit()
        return indicator
