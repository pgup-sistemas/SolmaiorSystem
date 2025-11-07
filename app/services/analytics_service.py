"""
Serviço de Analytics para Dashboard Macro
"""

from app import db
from app.models import (
    Student, Teacher, LessonSchedule, Payment, Enrollment, Room,
    Recital, SystemAnalytics
)
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta, date
from collections import defaultdict
import calendar


class AnalyticsService:
    """Serviço completo de analytics do sistema"""
    
    @staticmethod
    def get_dashboard_overview():
        """
        Retorna overview completo do dashboard
        
        Returns:
            dict: Estatísticas gerais do sistema
        """
        today = date.today()
        current_month_start = today.replace(day=1)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Estudantes
        total_students = Student.query.filter_by(is_active=True).count()
        new_students_this_month = Student.query.filter(
            Student.created_at >= current_month_start
        ).count()
        
        # Professores
        total_teachers = Teacher.query.filter_by(is_available=True).count()
        
        # Aulas
        lessons_this_month = LessonSchedule.query.filter(
            LessonSchedule.lesson_date >= current_month_start,
            LessonSchedule.lesson_date <= today
        ).count()
        
        lessons_last_month = LessonSchedule.query.filter(
            LessonSchedule.lesson_date >= last_month_start,
            LessonSchedule.lesson_date < current_month_start
        ).count()
        
        # Receita
        revenue_this_month = db.session.query(
            func.sum(Payment.total_amount)
        ).filter(
            Payment.status == 'paid',
            Payment.payment_date >= current_month_start
        ).scalar() or 0.0
        
        revenue_last_month = db.session.query(
            func.sum(Payment.total_amount)
        ).filter(
            Payment.status == 'paid',
            Payment.payment_date >= last_month_start,
            Payment.payment_date < current_month_start
        ).scalar() or 0.0
        
        # Calcular variações percentuais
        students_growth = AnalyticsService._calculate_growth(
            new_students_this_month, 
            total_students - new_students_this_month
        )
        
        lessons_growth = AnalyticsService._calculate_growth(
            lessons_this_month,
            lessons_last_month
        )
        
        revenue_growth = AnalyticsService._calculate_growth(
            revenue_this_month,
            revenue_last_month
        )
        
        # Frequência média
        confirmed_lessons = LessonSchedule.query.filter(
            LessonSchedule.lesson_date >= current_month_start,
            LessonSchedule.attendance_confirmed == True
        ).count()
        
        present_lessons = LessonSchedule.query.filter(
            LessonSchedule.lesson_date >= current_month_start,
            LessonSchedule.attendance_status == 'present'
        ).count()
        
        attendance_rate = (present_lessons / confirmed_lessons * 100) if confirmed_lessons > 0 else 0
        
        return {
            'students': {
                'total': total_students,
                'new_this_month': new_students_this_month,
                'growth': students_growth
            },
            'teachers': {
                'total': total_teachers
            },
            'lessons': {
                'this_month': lessons_this_month,
                'last_month': lessons_last_month,
                'growth': lessons_growth
            },
            'revenue': {
                'this_month': revenue_this_month,
                'last_month': revenue_last_month,
                'growth': revenue_growth
            },
            'attendance': {
                'rate': round(attendance_rate, 1)
            }
        }
    
    @staticmethod
    def _calculate_growth(current, previous):
        """Calcula crescimento percentual"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)
    
    @staticmethod
    def get_revenue_chart(months=6):
        """
        Gera dados para gráfico de receita
        
        Args:
            months: Número de meses para análise
        
        Returns:
            dict: Dados do gráfico
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=30 * months)
        
        payments = db.session.query(
            extract('year', Payment.payment_date).label('year'),
            extract('month', Payment.payment_date).label('month'),
            func.sum(Payment.total_amount).label('total')
        ).filter(
            Payment.status == 'paid',
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        labels = []
        values = []
        
        for p in payments:
            month_name = datetime(int(p.year), int(p.month), 1).strftime('%b/%y')
            labels.append(month_name)
            values.append(float(p.total))
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Receita (R$)',
                'data': values,
                'borderColor': 'rgb(59, 130, 246)',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'tension': 0.4
            }]
        }
    
    @staticmethod
    def get_students_by_instrument():
        """Gráfico de alunos por instrumento"""
        instruments = db.session.query(
            Student.instrument,
            func.count(Student.id).label('count')
        ).filter(
            Student.is_active == True
        ).group_by(Student.instrument).all()
        
        labels = [i.instrument for i in instruments]
        values = [i.count for i in instruments]
        
        colors = [
            'rgb(239, 68, 68)',   # red
            'rgb(59, 130, 246)',  # blue
            'rgb(34, 197, 94)',   # green
            'rgb(251, 146, 60)',  # orange
            'rgb(168, 85, 247)',  # purple
            'rgb(236, 72, 153)',  # pink
        ]
        
        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors[:len(values)]
            }]
        }
    
    @staticmethod
    def get_attendance_rate_chart(months=6):
        """Gráfico de taxa de frequência mensal"""
        end_date = date.today()
        start_date = end_date - timedelta(days=30 * months)
        
        # Buscar aulas por mês
        lessons_by_month = db.session.query(
            extract('year', LessonSchedule.lesson_date).label('year'),
            extract('month', LessonSchedule.lesson_date).label('month'),
            func.count(LessonSchedule.id).label('total'),
            func.sum(
                func.cast(LessonSchedule.attendance_status == 'present', db.Integer)
            ).label('present')
        ).filter(
            LessonSchedule.lesson_date >= start_date,
            LessonSchedule.lesson_date <= end_date,
            LessonSchedule.attendance_confirmed == True
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        labels = []
        values = []
        
        for l in lessons_by_month:
            month_name = datetime(int(l.year), int(l.month), 1).strftime('%b/%y')
            labels.append(month_name)
            
            rate = (l.present / l.total * 100) if l.total > 0 else 0
            values.append(round(rate, 1))
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Taxa de Presença (%)',
                'data': values,
                'borderColor': 'rgb(34, 197, 94)',
                'backgroundColor': 'rgba(34, 197, 94, 0.1)',
                'tension': 0.4
            }]
        }
    
    @staticmethod
    def get_lesson_distribution():
        """Distribuição de aulas por dia da semana"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        lessons = db.session.query(
            extract('dow', LessonSchedule.lesson_date).label('dow'),
            func.count(LessonSchedule.id).label('count')
        ).filter(
            LessonSchedule.lesson_date >= week_start,
            LessonSchedule.lesson_date <= week_end
        ).group_by('dow').all()
        
        days_pt = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        
        # Criar array com todos os dias
        data = [0] * 7
        for l in lessons:
            data[int(l.dow)] = l.count
        
        return {
            'labels': days_pt,
            'datasets': [{
                'label': 'Aulas por Dia',
                'data': data,
                'backgroundColor': 'rgb(59, 130, 246)'
            }]
        }
    
    @staticmethod
    def get_schedule_conflicts():
        """
        Detecta conflitos na agenda
        
        Returns:
            list: Lista de conflitos encontrados
        """
        today = date.today()
        week_end = today + timedelta(days=14)  # Próximas 2 semanas
        
        # Buscar aulas futuras
        lessons = LessonSchedule.query.filter(
            LessonSchedule.lesson_date >= today,
            LessonSchedule.lesson_date <= week_end,
            LessonSchedule.status == 'scheduled'
        ).order_by(
            LessonSchedule.lesson_date,
            LessonSchedule.start_time
        ).all()
        
        conflicts = []
        
        # Verificar conflitos de professor
        teacher_schedule = defaultdict(list)
        for lesson in lessons:
            key = (lesson.teacher_id, lesson.lesson_date, lesson.start_time)
            teacher_schedule[key].append(lesson)
        
        for key, lesson_list in teacher_schedule.items():
            if len(lesson_list) > 1:
                conflicts.append({
                    'type': 'teacher',
                    'severity': 'high',
                    'date': lesson_list[0].lesson_date,
                    'time': lesson_list[0].start_time,
                    'teacher': lesson_list[0].teacher.user.full_name,
                    'lessons': [
                        {
                            'id': l.id,
                            'student': l.student.user.full_name,
                            'room': l.room.name if l.room else 'Não definida'
                        }
                        for l in lesson_list
                    ]
                })
        
        # Verificar conflitos de sala
        room_schedule = defaultdict(list)
        for lesson in lessons:
            if lesson.room_id:
                key = (lesson.room_id, lesson.lesson_date, lesson.start_time)
                room_schedule[key].append(lesson)
        
        for key, lesson_list in room_schedule.items():
            if len(lesson_list) > 1:
                conflicts.append({
                    'type': 'room',
                    'severity': 'medium',
                    'date': lesson_list[0].lesson_date,
                    'time': lesson_list[0].start_time,
                    'room': lesson_list[0].room.name,
                    'lessons': [
                        {
                            'id': l.id,
                            'student': l.student.user.full_name,
                            'teacher': l.teacher.user.full_name
                        }
                        for l in lesson_list
                    ]
                })
        
        # Verificar conflitos de aluno
        student_schedule = defaultdict(list)
        for lesson in lessons:
            key = (lesson.student_id, lesson.lesson_date, lesson.start_time)
            student_schedule[key].append(lesson)
        
        for key, lesson_list in student_schedule.items():
            if len(lesson_list) > 1:
                conflicts.append({
                    'type': 'student',
                    'severity': 'low',
                    'date': lesson_list[0].lesson_date,
                    'time': lesson_list[0].start_time,
                    'student': lesson_list[0].student.user.full_name,
                    'lessons': [
                        {
                            'id': l.id,
                            'teacher': l.teacher.user.full_name,
                            'room': l.room.name if l.room else 'Não definida'
                        }
                        for l in lesson_list
                    ]
                })
        
        return conflicts
    
    @staticmethod
    def get_room_occupancy(days=7):
        """
        Calcula taxa de ocupação das salas
        
        Args:
            days: Número de dias para análise
        
        Returns:
            list: Taxa de ocupação por sala
        """
        start_date = date.today()
        end_date = start_date + timedelta(days=days)
        
        rooms = Room.query.filter_by(is_available=True).all()
        occupancy_data = []
        
        # Horas úteis: 8h às 20h = 12 horas por dia
        total_hours = days * 12
        
        for room in rooms:
            # Contar horas agendadas
            lessons = LessonSchedule.query.filter(
                LessonSchedule.room_id == room.id,
                LessonSchedule.lesson_date >= start_date,
                LessonSchedule.lesson_date <= end_date,
                LessonSchedule.status == 'scheduled'
            ).all()
            
            total_minutes = 0
            for lesson in lessons:
                # Calcular duração da aula
                start = datetime.combine(date.today(), lesson.start_time)
                end = datetime.combine(date.today(), lesson.end_time)
                duration = (end - start).total_seconds() / 60
                total_minutes += duration
            
            occupied_hours = total_minutes / 60
            occupancy_rate = (occupied_hours / total_hours * 100) if total_hours > 0 else 0
            
            occupancy_data.append({
                'room': room.name,
                'occupancy_rate': round(occupancy_rate, 1),
                'occupied_hours': round(occupied_hours, 1),
                'total_hours': total_hours,
                'lessons_count': len(lessons)
            })
        
        return occupancy_data
    
    @staticmethod
    def get_payment_status_summary():
        """Resumo do status de pagamentos"""
        current_month = date.today().replace(day=1)
        
        summary = db.session.query(
            Payment.status,
            func.count(Payment.id).label('count'),
            func.sum(Payment.total_amount).label('total')
        ).filter(
            Payment.reference_month >= current_month
        ).group_by(Payment.status).all()
        
        status_map = {
            'pending': 'Pendente',
            'paid': 'Pago',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado'
        }
        
        result = []
        for s in summary:
            result.append({
                'status': status_map.get(s.status, s.status),
                'count': s.count,
                'total': float(s.total or 0)
            })
        
        return result
    
    @staticmethod
    def save_analytics_snapshot():
        """
        Salva snapshot das métricas atuais para histórico
        
        Returns:
            dict: Confirmação
        """
        today = date.today()
        
        overview = AnalyticsService.get_dashboard_overview()
        
        # Salvar métricas principais
        metrics = [
            ('students', 'Total de Alunos', overview['students']['total']),
            ('teachers', 'Total de Professores', overview['teachers']['total']),
            ('revenue', 'Receita Mensal', overview['revenue']['this_month']),
            ('attendance', 'Taxa de Frequência', overview['attendance']['rate']),
        ]
        
        for metric_type, metric_name, value in metrics:
            analytics = SystemAnalytics(
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                period_type='daily',
                period_start=today,
                period_end=today
            )
            db.session.add(analytics)
        
        db.session.commit()
        
        return {'success': True, 'metrics_saved': len(metrics)}
