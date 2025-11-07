"""
Serviço de geração de PDFs para recitais, certificados e programas
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import os


class RecitalPDFGenerator:
    """Gerador de PDFs para recitais"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Texto de certificado
        self.styles.add(ParagraphStyle(
            name='CertificateText',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            leading=20
        ))
        
        # Assinatura
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=5
        ))
    
    def generate_recital_program(self, recital, performances):
        """
        Gera o programa do recital em PDF
        
        Args:
            recital: Objeto Recital
            performances: Lista de RecitalPerformance
        
        Returns:
            BytesIO: PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Cabeçalho
        title = Paragraph(f"<b>{recital.title}</b>", self.styles['CustomTitle'])
        story.append(title)
        
        # Data e local
        event_date = recital.event_date.strftime('%d/%m/%Y às %H:%M')
        subtitle = Paragraph(
            f"<b>{event_date}</b><br/>{recital.location or 'Escola de Música Sol Maior'}",
            self.styles['CustomSubtitle']
        )
        story.append(subtitle)
        story.append(Spacer(1, 0.5*inch))
        
        # Descrição do evento
        if recital.description:
            desc = Paragraph(recital.description, self.styles['Normal'])
            story.append(desc)
            story.append(Spacer(1, 0.3*inch))
        
        # Programa
        program_title = Paragraph("<b>PROGRAMA</b>", self.styles['Heading2'])
        story.append(program_title)
        story.append(Spacer(1, 0.2*inch))
        
        # Listar performances
        for idx, performance in enumerate(sorted(performances, key=lambda x: x.order_number or 0), 1):
            # Tipo de apresentação
            type_map = {
                'solo': 'Solo',
                'duo': 'Duo',
                'group': 'Grupo',
                'choir': 'Coral',
                'band': 'Banda'
            }
            perf_type = type_map.get(performance.performance_type, performance.performance_type)
            
            # Participantes
            participants = []
            for p in performance.participants:
                if p.student_id:
                    name = p.student.user.full_name
                    role = p.role or 'Performer'
                    participants.append(f"{name} ({role})")
                elif p.teacher_id:
                    name = p.teacher.user.full_name
                    role = p.role or 'Professor'
                    participants.append(f"{name} ({role})")
            
            participants_text = ", ".join(participants)
            
            # Montar texto da performance
            perf_text = f"""
            <b>{idx}. {performance.piece_title}</b><br/>
            {performance.composer or 'Compositor não informado'}<br/>
            <i>{perf_type}</i> - {participants_text}
            """
            
            if performance.duration_minutes:
                perf_text += f"<br/>Duração: {performance.duration_minutes} minutos"
            
            story.append(Paragraph(perf_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Rodapé
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            "Escola de Música Sol Maior<br/>www.solmaior.com.br",
            self.styles['CustomSubtitle']
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_certificate(self, recital, participant, performance):
        """
        Gera certificado de participação em PDF
        
        Args:
            recital: Objeto Recital
            participant: Objeto RecitalParticipant
            performance: Objeto RecitalPerformance
        
        Returns:
            BytesIO: PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            topMargin=1.5*inch,
            bottomMargin=1.5*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        story = []
        
        # Borda decorativa (opcional)
        story.append(Spacer(1, 0.3*inch))
        
        # Título
        title = Paragraph("<b>CERTIFICADO DE PARTICIPAÇÃO</b>", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Nome do participante
        if participant.student_id:
            participant_name = participant.student.user.full_name
        else:
            participant_name = participant.teacher.user.full_name
        
        # Texto do certificado
        event_date = recital.event_date.strftime('%d de %B de %Y')
        
        cert_text = f"""
        Certificamos que <b>{participant_name}</b> participou do recital 
        <b>"{recital.title}"</b>, realizado em {event_date}, 
        apresentando a obra <b>"{performance.piece_title}"</b>
        {f'de {performance.composer}' if performance.composer else ''} 
        na modalidade <i>{performance.performance_type}</i>.
        """
        
        cert_paragraph = Paragraph(cert_text, self.styles['CertificateText'])
        story.append(cert_paragraph)
        story.append(Spacer(1, 1*inch))
        
        # Assinaturas
        sig_data = [
            ['_' * 30, '', '_' * 30],
            ['Coordenação Pedagógica', '', 'Direção']
        ]
        
        sig_table = Table(sig_data, colWidths=[2.5*inch, 0.5*inch, 2.5*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 5),
        ]))
        
        story.append(sig_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Data de emissão
        issue_date = datetime.now().strftime('%d/%m/%Y')
        footer = Paragraph(
            f"São Paulo, {issue_date}<br/>Escola de Música Sol Maior",
            self.styles['Signature']
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer


class AnalyticsChartGenerator:
    """Gerador de gráficos para analytics"""
    
    @staticmethod
    def generate_revenue_chart_data(start_date, end_date):
        """Gera dados para gráfico de receita"""
        from app import db
        from app.models import Payment
        from sqlalchemy import func, extract
        
        payments = db.session.query(
            extract('year', Payment.reference_month).label('year'),
            extract('month', Payment.reference_month).label('month'),
            func.sum(Payment.total_amount).label('total')
        ).filter(
            Payment.status == 'paid',
            Payment.reference_month >= start_date,
            Payment.reference_month <= end_date
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        labels = []
        values = []
        
        for p in payments:
            month_name = datetime(int(p.year), int(p.month), 1).strftime('%b/%Y')
            labels.append(month_name)
            values.append(float(p.total))
        
        return {'labels': labels, 'values': values}
    
    @staticmethod
    def generate_attendance_chart_data(start_date, end_date):
        """Gera dados para gráfico de frequência"""
        from app import db
        from app.models import LessonSchedule
        from sqlalchemy import func
        
        attendance = db.session.query(
            LessonSchedule.attendance_status,
            func.count(LessonSchedule.id).label('count')
        ).filter(
            LessonSchedule.lesson_date >= start_date,
            LessonSchedule.lesson_date <= end_date,
            LessonSchedule.attendance_confirmed == True
        ).group_by(LessonSchedule.attendance_status).all()
        
        status_map = {
            'present': 'Presente',
            'absent': 'Falta',
            'late': 'Atrasado',
            'justified': 'Justificado'
        }
        
        labels = []
        values = []
        
        for a in attendance:
            if a.attendance_status:
                labels.append(status_map.get(a.attendance_status, a.attendance_status))
                values.append(a.count)
        
        return {'labels': labels, 'values': values}
    
    @staticmethod
    def generate_students_by_instrument_data():
        """Gera dados de alunos por instrumento"""
        from app import db
        from app.models import Student
        from sqlalchemy import func
        
        instruments = db.session.query(
            Student.instrument,
            func.count(Student.id).label('count')
        ).filter(
            Student.is_active == True
        ).group_by(Student.instrument).all()
        
        labels = [i.instrument for i in instruments]
        values = [i.count for i in instruments]
        
        return {'labels': labels, 'values': values}
