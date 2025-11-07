from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models import NewsPost, TrialLesson, LandingPageContent, LandingPageFeature

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    # Buscar conteúdo dinâmico da landing page
    hero = LandingPageContent.query.filter_by(section='hero', is_active=True).first()
    about = LandingPageContent.query.filter_by(section='about', is_active=True).first()
    cta = LandingPageContent.query.filter_by(section='cta', is_active=True).first()
    features = LandingPageFeature.query.filter_by(is_active=True).order_by(LandingPageFeature.display_order).all()
    
    # Buscar notícias
    news = NewsPost.query.filter_by(is_published=True).order_by(NewsPost.published_at.desc()).limit(3).all()
    
    return render_template('public/index.html', 
                         news=news,
                         hero=hero,
                         about=about,
                         cta=cta,
                         features=features)

@bp.route('/about')
def about():
    return render_template('public/about.html')

@bp.route('/trial-lesson', methods=['GET', 'POST'])
def trial_lesson():
    if request.method == 'POST':
        from app.tasks import send_email
        from datetime import datetime
        
        trial = TrialLesson(
            full_name=request.form.get('full_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            instrument=request.form.get('instrument'),
            message=request.form.get('message')
        )
        
        db.session.add(trial)
        db.session.commit()
        
        # Enviar email de confirmação para o usuário
        send_trial_request_confirmation_email(trial)
        
        # Enviar notificação para admin/secretaria
        send_trial_request_notification_to_admin(trial)
        
        flash('Solicitação enviada com sucesso! Você receberá um email de confirmação em breve.', 'success')
        return redirect(url_for('public.index'))
    
    return render_template('public/trial_lesson.html')


def send_trial_request_confirmation_email(trial):
    """Enviar email de confirmação ao usuário que solicitou"""
    from app.tasks import send_email
    
    try:
        subject = f'✅ Solicitação de Aula Experimental Recebida - {trial.instrument}'
        
        message = f"""Olá {trial.full_name},

Recebemos sua solicitação de aula experimental! 🎉

📋 DADOS DA SOLICITAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Instrumento: {trial.instrument}
📞 Telefone: {trial.phone}
📧 Email: {trial.email}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 PRÓXIMOS PASSOS:

• Nossa equipe analisará sua solicitação
• Entraremos em contato em até 24 horas
• Você receberá informações sobre disponibilidade
• Após agendamento, enviaremos confirmação com data e horário

💡 DICA: Mantenha seu telefone {trial.phone} disponível para contato!

Se tiver alguma dúvida, responda este email ou entre em contato conosco.

Atenciosamente,
Escola de Música Sol Maior

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Solicitação #{trial.id} | {trial.created_at.strftime('%d/%m/%Y %H:%M')}
"""
        
        return send_email(trial.email, subject, message)
        
    except Exception as e:
        print(f'Erro ao enviar email de confirmação: {str(e)}')
        return False


def send_trial_request_notification_to_admin(trial):
    """Enviar notificação para admin e secretaria sobre nova solicitação"""
    from app.tasks import send_email
    from app.models import User
    
    try:
        # Buscar admin e secretaria
        admins = User.query.filter(User.role.in_(['admin', 'secretary']), User.is_active == True).all()
        
        subject = f'🔔 Nova Solicitação de Aula Experimental - {trial.instrument}'
        
        message = f"""Nova solicitação de aula experimental recebida!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 DADOS DO INTERESSADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Nome: {trial.full_name}
📧 Email: {trial.email}
📞 Telefone: {trial.phone}
🎵 Instrumento: {trial.instrument}

💬 Mensagem:
{trial.message if trial.message else 'Nenhuma mensagem adicional'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Solicitado em: {trial.created_at.strftime('%d/%m/%Y às %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ AÇÃO NECESSÁRIA:

Entre em contato com o interessado o mais breve possível e
agende a aula experimental no sistema.

Acesse: http://localhost:5000/trial-lessons/{trial.id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Solicitação #{trial.id}
"""
        
        # Enviar para todos admins/secretaria
        for admin in admins:
            send_email(admin.email, subject, message)
        
        return True
        
    except Exception as e:
        print(f'Erro ao enviar notificação para admin: {str(e)}')
        return False

@bp.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    news_posts = NewsPost.query.filter_by(is_published=True).order_by(NewsPost.published_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('public/news.html', news=news_posts)

@bp.route('/news/<int:id>')
def news_detail(id):
    post = NewsPost.query.get_or_404(id)
    return render_template('public/news_detail.html', post=post)
