"""
Serviço de automação de recitais (convites, certificados, etc)
"""

from app import db
from app.models import (
    Recital, RecitalParticipant, RecitalInvitation, RecitalCertificate,
    ScheduledNotification, Student, Teacher
)
from datetime import datetime, timedelta
import secrets
import string


class RecitalService:
    """Serviço para automação de recitals"""
    
    @staticmethod
    def generate_invitation_token():
        """Gera token único para convite"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def send_recital_invitations(recital_id):
        """
        Envia convites automáticos para todos os participantes de um recital
        
        Args:
            recital_id: ID do recital
        
        Returns:
            dict: Resultado da operação com contadores
        """
        recital = Recital.query.get_or_404(recital_id)
        
        # Buscar todos os participantes
        participants = db.session.query(RecitalParticipant).join(
            RecitalParticipant.performance
        ).filter(
            RecitalParticipant.performance.has(recital_id=recital_id)
        ).all()
        
        invitations_created = 0
        invitations_sent = 0
        
        for participant in participants:
            # Verificar se já existe convite
            existing_invitation = RecitalInvitation.query.filter_by(
                recital_id=recital_id,
                participant_id=participant.id
            ).first()
            
            if existing_invitation:
                continue
            
            # Obter email do participante
            if participant.student_id:
                email = participant.student.user.email
                name = participant.student.user.full_name
            else:
                email = participant.teacher.user.email
                name = participant.teacher.user.full_name
            
            # Criar convite
            invitation = RecitalInvitation(
                recital_id=recital_id,
                participant_id=participant.id,
                email=email,
                invitation_token=RecitalService.generate_invitation_token(),
                status='pending'
            )
            
            db.session.add(invitation)
            invitations_created += 1
            
            # Agendar notificação
            notification = ScheduledNotification(
                notification_type='recital_invitation',
                recipient_id=participant.student.user_id if participant.student_id else participant.teacher.user_id,
                recipient_email=email,
                subject=f'Convite: {recital.title}',
                message=RecitalService._generate_invitation_email(recital, participant, invitation.invitation_token),
                scheduled_for=datetime.utcnow(),
                status='pending'
            )
            
            db.session.add(notification)
            invitations_sent += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'invitations_created': invitations_created,
            'invitations_sent': invitations_sent,
            'total_participants': len(participants)
        }
    
    @staticmethod
    def _generate_invitation_email(recital, participant, token):
        """Gera corpo do email de convite"""
        if participant.student_id:
            name = participant.student.user.full_name
        else:
            name = participant.teacher.user.full_name
        
        event_date = recital.event_date.strftime('%d/%m/%Y às %H:%M')
        
        message = f"""
Olá {name},

Você está convidado(a) para participar do recital:

{recital.title}
Data: {event_date}
Local: {recital.location or 'Escola de Música Sol Maior'}

{recital.description or ''}

Por favor, confirme sua presença através do link abaixo:
[LINK DE CONFIRMAÇÃO]

Estamos ansiosos para contar com sua participação!

Atenciosamente,
Equipe Sol Maior
        """
        
        return message.strip()
    
    @staticmethod
    def confirm_invitation(token):
        """
        Confirma presença através do token de convite
        
        Args:
            token: Token do convite
        
        Returns:
            dict: Resultado da operação
        """
        invitation = RecitalInvitation.query.filter_by(
            invitation_token=token
        ).first()
        
        if not invitation:
            return {'success': False, 'error': 'Convite não encontrado'}
        
        if invitation.status == 'confirmed':
            return {'success': False, 'error': 'Convite já confirmado anteriormente'}
        
        # Confirmar convite
        invitation.status = 'confirmed'
        invitation.confirmed_at = datetime.utcnow()
        
        # Confirmar participante
        participant = invitation.participant
        participant.confirmed = True
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Presença confirmada com sucesso!',
            'recital': invitation.recital
        }
    
    @staticmethod
    def decline_invitation(token):
        """Declina convite através do token"""
        invitation = RecitalInvitation.query.filter_by(
            invitation_token=token
        ).first()
        
        if not invitation:
            return {'success': False, 'error': 'Convite não encontrado'}
        
        invitation.status = 'declined'
        participant = invitation.participant
        participant.confirmed = False
        
        db.session.commit()
        
        return {'success': True, 'message': 'Convite declinado'}
    
    @staticmethod
    def generate_certificates(recital_id):
        """
        Gera certificados para todos os participantes confirmados
        
        Args:
            recital_id: ID do recital
        
        Returns:
            dict: Resultado com número de certificados gerados
        """
        from app.services.pdf_generator import RecitalPDFGenerator
        import os
        
        recital = Recital.query.get_or_404(recital_id)
        
        # Verificar se recital foi concluído
        if recital.status != 'completed':
            return {
                'success': False,
                'error': 'Apenas recitais concluídos podem ter certificados gerados'
            }
        
        # Buscar participantes confirmados
        participants = db.session.query(RecitalParticipant).join(
            RecitalParticipant.performance
        ).filter(
            RecitalParticipant.performance.has(recital_id=recital_id),
            RecitalParticipant.confirmed == True
        ).all()
        
        pdf_gen = RecitalPDFGenerator()
        certificates_generated = 0
        
        # Criar diretório de certificados se não existir
        cert_dir = os.path.join('app', 'static', 'certificates')
        os.makedirs(cert_dir, exist_ok=True)
        
        for participant in participants:
            # Verificar se já existe certificado
            existing_cert = RecitalCertificate.query.filter_by(
                recital_id=recital_id,
                participant_id=participant.id
            ).first()
            
            if existing_cert:
                continue
            
            # Gerar número único de certificado
            cert_number = f"CERT-{recital_id}-{participant.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Gerar PDF
            pdf_buffer = pdf_gen.generate_certificate(
                recital,
                participant,
                participant.performance
            )
            
            # Salvar arquivo
            filename = f"{cert_number}.pdf"
            filepath = os.path.join(cert_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            # Criar registro no banco
            certificate = RecitalCertificate(
                recital_id=recital_id,
                participant_id=participant.id,
                certificate_number=cert_number,
                file_path=filepath
            )
            
            db.session.add(certificate)
            certificates_generated += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'certificates_generated': certificates_generated,
            'total_participants': len(participants)
        }
    
    @staticmethod
    def send_reminders(recital_id, days_before=3):
        """
        Envia lembretes para participantes confirmados
        
        Args:
            recital_id: ID do recital
            days_before: Dias antes do evento
        
        Returns:
            dict: Resultado
        """
        recital = Recital.query.get_or_404(recital_id)
        
        # Verificar se está no período de envio
        days_until = (recital.event_date.date() - datetime.now().date()).days
        
        if days_until != days_before:
            return {
                'success': False,
                'error': f'Lembretes serão enviados {days_before} dias antes do evento'
            }
        
        # Buscar convites confirmados sem lembrete
        invitations = RecitalInvitation.query.filter_by(
            recital_id=recital_id,
            status='confirmed',
            reminder_sent=False
        ).all()
        
        reminders_sent = 0
        
        for invitation in invitations:
            participant = invitation.participant
            
            if participant.student_id:
                recipient_id = participant.student.user_id
                name = participant.student.user.full_name
            else:
                recipient_id = participant.teacher.user_id
                name = participant.teacher.user.full_name
            
            event_date = recital.event_date.strftime('%d/%m/%Y às %H:%M')
            
            message = f"""
Olá {name},

Este é um lembrete sobre o recital:

{recital.title}
Data: {event_date}
Local: {recital.location or 'Escola de Música Sol Maior'}

Sua presença está confirmada. Nos vemos lá!

Atenciosamente,
Equipe Sol Maior
            """
            
            # Agendar notificação
            notification = ScheduledNotification(
                notification_type='recital_reminder',
                recipient_id=recipient_id,
                recipient_email=invitation.email,
                subject=f'Lembrete: {recital.title}',
                message=message.strip(),
                scheduled_for=datetime.utcnow(),
                status='pending'
            )
            
            db.session.add(notification)
            
            invitation.reminder_sent = True
            reminders_sent += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'reminders_sent': reminders_sent
        }
