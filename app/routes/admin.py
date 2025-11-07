from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    User, Teacher, Student, Room, LessonSchedule, Recital, NewsPost, TrialLesson, 
    TeacherAvailability, RecitalPerformance, RecitalParticipant, LandingPageContent,
    LandingPageFeature, RecitalInvitation, RecitalCertificate
)
from app.services.analytics_service import AnalyticsService
from app.services.recital_service import RecitalService
from app.services.pdf_generator import RecitalPDFGenerator
from datetime import datetime, timedelta
from io import BytesIO

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Estatísticas básicas
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_rooms = Room.query.count()
    pending_trials = TrialLesson.query.filter_by(status='pending').count()
    
    # Analytics completo
    analytics = AnalyticsService.get_dashboard_overview()
    
    # Gráficos
    revenue_chart = AnalyticsService.get_revenue_chart(months=6)
    students_chart = AnalyticsService.get_students_by_instrument()
    attendance_chart = AnalyticsService.get_attendance_rate_chart(months=6)
    lesson_distribution = AnalyticsService.get_lesson_distribution()
    
    # Conflitos de agenda
    conflicts = AnalyticsService.get_schedule_conflicts()
    
    # Ocupação de salas
    room_occupancy = AnalyticsService.get_room_occupancy(days=7)
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_rooms=total_rooms,
                         pending_trials=pending_trials,
                         analytics=analytics,
                         revenue_chart=revenue_chart,
                         students_chart=students_chart,
                         attendance_chart=attendance_chart,
                         lesson_distribution=lesson_distribution,
                         conflicts=conflicts,
                         room_occupancy=room_occupancy)

@bp.route('/global-schedule')
@login_required
@admin_required
def global_schedule():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    lessons = LessonSchedule.query.filter(
        LessonSchedule.lesson_date >= week_start,
        LessonSchedule.lesson_date <= week_end
    ).all()
    
    teachers = Teacher.query.all()
    rooms = Room.query.all()
    
    return render_template('admin/global_schedule.html',
                         lessons=lessons,
                         teachers=teachers,
                         rooms=rooms,
                         week_start=week_start)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role')
        
        if not email or not password or not full_name or not role:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return redirect(url_for('admin.create_user'))
        
        try:
            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()
            
            if role == 'teacher':
                teacher = Teacher(
                    user_id=user.id,
                    instrument=request.form.get('instrument', 'Não especificado'),
                    specialization=request.form.get('specialization', '')
                )
                db.session.add(teacher)
            elif role == 'student':
                student = Student(
                    user_id=user.id,
                    instrument=request.form.get('instrument', 'Não especificado'),
                    level=request.form.get('level', 'Iniciante')
                )
                db.session.add(student)
            
            db.session.commit()
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
            return redirect(url_for('admin.create_user'))
    
    return render_template('admin/create_user.html')

@bp.route('/rooms')
@login_required
@admin_required
def rooms():
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)

@bp.route('/rooms/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_room():
    if request.method == 'POST':
        room = Room(
            name=request.form.get('name'),
            capacity=request.form.get('capacity', type=int),
            equipment=request.form.get('equipment')
        )
        
        db.session.add(room)
        db.session.commit()
        
        flash('Sala criada com sucesso!', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/create_room.html')

@bp.route('/recitals')
@login_required
@admin_required
def recitals():
    recitals = Recital.query.order_by(Recital.event_date.desc()).all()
    return render_template('admin/recitals.html', recitals=recitals)

@bp.route('/recitals/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_recital():
    if request.method == 'POST':
        recital = Recital(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M'),
            location=request.form.get('location'),
            created_by=current_user.id
        )
        
        db.session.add(recital)
        db.session.commit()
        
        flash('Recital criado com sucesso!', 'success')
        return redirect(url_for('admin.recitals'))
    
    return render_template('admin/create_recital.html')

@bp.route('/news')
@login_required
@admin_required
def news():
    posts = NewsPost.query.order_by(NewsPost.created_at.desc()).all()
    return render_template('admin/news.html', posts=posts)

@bp.route('/news/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_news():
    if request.method == 'POST':
        post = NewsPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author_id=current_user.id,
            post_type=request.form.get('post_type', 'news'),
            is_published=request.form.get('is_published') == 'on'
        )
        
        if post.is_published:
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Notícia criada com sucesso!', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/create_news.html')

@bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_news(id):
    post = NewsPost.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.post_type = request.form.get('post_type', 'news')
        
        was_published = post.is_published
        post.is_published = request.form.get('is_published') == 'on'
        
        if post.is_published and not was_published:
            post.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('Notícia atualizada com sucesso!', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/edit_news.html', post=post)

@bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_news(id):
    post = NewsPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Notícia excluída com sucesso!', 'success')
    return redirect(url_for('admin.news'))

@bp.route('/trial-lessons')
@login_required
@admin_required
def trial_lessons():
    trials = TrialLesson.query.order_by(TrialLesson.created_at.desc()).all()
    return render_template('admin/trial_lessons.html', trials=trials)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.is_active = request.form.get('is_active') == 'on'
        
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('Você não pode excluir seu próprio usuário!', 'error')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        student.instrument = request.form.get('instrument')
        student.level = request.form.get('level')
        student.guardian_name = request.form.get('guardian_name')
        student.guardian_phone = request.form.get('guardian_phone')
        student.guardian_email = request.form.get('guardian_email')
        student.guardian_cpf = request.form.get('guardian_cpf')
        student.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
        student.cpf = request.form.get('cpf')
        student.rg = request.form.get('rg')
        student.address = request.form.get('address')
        student.city = request.form.get('city')
        student.state = request.form.get('state')
        student.zip_code = request.form.get('zip_code')
        student.course_modality = request.form.get('course_modality')
        student.weekly_lessons = request.form.get('weekly_lessons', type=int)
        student.lesson_duration = request.form.get('lesson_duration', type=int)
        student.preferred_schedule = request.form.get('preferred_schedule')
        student.medical_info = request.form.get('medical_info')
        student.special_needs = request.form.get('special_needs')
        student.previous_experience = request.form.get('previous_experience')
        student.goals = request.form.get('goals')
        student.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Dados do aluno atualizados com sucesso!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_student.html', student=student)


# ============================================================================
# ROTAS AVANÇADAS DE RECITALS
# ============================================================================

@bp.route('/recitals/<int:id>')
@login_required
@admin_required
def recital_detail(id):
    """Visualizar detalhes completos do recital"""
    recital = Recital.query.get_or_404(id)
    performances = RecitalPerformance.query.filter_by(recital_id=id).order_by(RecitalPerformance.order_number).all()
    invitations = RecitalInvitation.query.filter_by(recital_id=id).all()
    certificates = RecitalCertificate.query.filter_by(recital_id=id).all()
    
    return render_template('admin/recital_detail.html',
                         recital=recital,
                         performances=performances,
                         invitations=invitations,
                         certificates=certificates)

@bp.route('/recitals/<int:id>/add-performance', methods=['GET', 'POST'])
@login_required
@admin_required
def add_performance(id):
    """Adicionar performance ao recital"""
    recital = Recital.query.get_or_404(id)
    
    if request.method == 'POST':
        performance = RecitalPerformance(
            recital_id=id,
            performance_type=request.form.get('performance_type'),
            piece_title=request.form.get('piece_title'),
            composer=request.form.get('composer'),
            duration_minutes=request.form.get('duration_minutes', type=int),
            order_number=request.form.get('order_number', type=int)
        )
        
        db.session.add(performance)
        db.session.flush()
        
        # Adicionar participantes
        student_ids = request.form.getlist('student_ids')
        teacher_ids = request.form.getlist('teacher_ids')
        
        for student_id in student_ids:
            if student_id:
                participant = RecitalParticipant(
                    performance_id=performance.id,
                    student_id=int(student_id),
                    role='performer'
                )
                db.session.add(participant)
        
        for teacher_id in teacher_ids:
            if teacher_id:
                participant = RecitalParticipant(
                    performance_id=performance.id,
                    teacher_id=int(teacher_id),
                    role='accompanist'
                )
                db.session.add(participant)
        
        db.session.commit()
        flash('Performance adicionada com sucesso!', 'success')
        return redirect(url_for('admin.recital_detail', id=id))
    
    students = Student.query.filter_by(is_active=True).all()
    teachers = Teacher.query.filter_by(is_available=True).all()
    
    return render_template('admin/add_performance.html',
                         recital=recital,
                         students=students,
                         teachers=teachers)

@bp.route('/recitals/<int:id>/send-invitations', methods=['POST'])
@login_required
@admin_required
def send_recital_invitations(id):
    """Enviar convites automáticos para todos os participantes"""
    result = RecitalService.send_recital_invitations(id)
    
    if result['success']:
        flash(f"Convites enviados! {result['invitations_sent']} notificações agendadas.", 'success')
    else:
        flash('Erro ao enviar convites.', 'error')
    
    return redirect(url_for('admin.recital_detail', id=id))

@bp.route('/recitals/<int:id>/generate-program')
@login_required
@admin_required
def generate_recital_program(id):
    """Gerar PDF do programa do recital"""
    recital = Recital.query.get_or_404(id)
    performances = RecitalPerformance.query.filter_by(recital_id=id).order_by(RecitalPerformance.order_number).all()
    
    pdf_gen = RecitalPDFGenerator()
    pdf_buffer = pdf_gen.generate_recital_program(recital, performances)
    
    filename = f"Programa_{recital.title.replace(' ', '_')}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@bp.route('/recitals/<int:id>/generate-certificates', methods=['POST'])
@login_required
@admin_required
def generate_recital_certificates(id):
    """Gerar certificados para todos os participantes"""
    result = RecitalService.generate_certificates(id)
    
    if result['success']:
        flash(f"Certificados gerados! {result['certificates_generated']} certificados criados.", 'success')
    else:
        flash(f"Erro: {result.get('error')}", 'error')
    
    return redirect(url_for('admin.recital_detail', id=id))

@bp.route('/recitals/<int:id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_recital(id):
    """Marcar recital como concluído"""
    recital = Recital.query.get_or_404(id)
    recital.status = 'completed'
    db.session.commit()
    
    flash('Recital marcado como concluído!', 'success')
    return redirect(url_for('admin.recital_detail', id=id))


# ============================================================================
# ROTAS DE LANDING PAGE DINÂMICA
# ============================================================================

@bp.route('/landing-page')
@login_required
@admin_required
def landing_page_settings():
    """Configurações da landing page - Dashboard principal"""
    from app.models import PublicAnnouncement, LandingPageTestimonial, LandingPageGallery
    
    # Seções de conteúdo
    hero = LandingPageContent.query.filter_by(section='hero').first()
    about = LandingPageContent.query.filter_by(section='about').first()
    cta = LandingPageContent.query.filter_by(section='cta').first()
    features = LandingPageFeature.query.order_by(LandingPageFeature.display_order).all()
    
    # Avisos e anúncios
    announcements = PublicAnnouncement.query.order_by(
        PublicAnnouncement.priority.desc(),
        PublicAnnouncement.created_at.desc()
    ).limit(10).all()
    
    # Depoimentos
    testimonials = LandingPageTestimonial.query.order_by(
        LandingPageTestimonial.display_order
    ).all()
    
    # Galeria
    gallery_images = LandingPageGallery.query.filter_by(is_featured=True).limit(6).all()
    
    # Estatísticas
    stats = {
        'total_announcements': PublicAnnouncement.query.count(),
        'active_announcements': PublicAnnouncement.query.filter_by(is_active=True).count(),
        'total_testimonials': LandingPageTestimonial.query.count(),
        'total_gallery': LandingPageGallery.query.count(),
        'total_features': LandingPageFeature.query.count()
    }
    
    return render_template('admin/landing_page.html',
                         hero=hero,
                         about=about,
                         cta=cta,
                         features=features,
                         announcements=announcements,
                         testimonials=testimonials,
                         gallery_images=gallery_images,
                         stats=stats)

@bp.route('/landing-page/section/<section>', methods=['POST'])
@login_required
@admin_required
def update_landing_section(section):
    """Atualizar seção da landing page"""
    content = LandingPageContent.query.filter_by(section=section).first()
    
    if not content:
        content = LandingPageContent(section=section)
        db.session.add(content)
    
    content.title = request.form.get('title')
    content.subtitle = request.form.get('subtitle')
    content.content = request.form.get('content')
    content.button_text = request.form.get('button_text')
    content.button_link = request.form.get('button_link')
    content.is_active = request.form.get('is_active') == 'on'
    content.updated_by = current_user.id
    
    db.session.commit()
    
    flash(f'Seção {section} atualizada com sucesso!', 'success')
    return redirect(url_for('admin.landing_page_settings'))

@bp.route('/landing-page/features/add', methods=['POST'])
@login_required
@admin_required
def add_landing_feature():
    """Adicionar feature/card à landing page"""
    feature = LandingPageFeature(
        icon=request.form.get('icon'),
        title=request.form.get('title'),
        description=request.form.get('description'),
        display_order=request.form.get('display_order', type=int, default=0),
        is_active=True
    )
    
    db.session.add(feature)
    db.session.commit()
    
    flash('Feature adicionada com sucesso!', 'success')
    return redirect(url_for('admin.landing_page_settings'))

@bp.route('/landing-page/features/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_landing_feature(id):
    """Editar feature da landing page"""
    feature = LandingPageFeature.query.get_or_404(id)
    
    feature.icon = request.form.get('icon')
    feature.title = request.form.get('title')
    feature.description = request.form.get('description')
    feature.display_order = request.form.get('display_order', type=int)
    feature.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    
    flash('Feature atualizada com sucesso!', 'success')
    return redirect(url_for('admin.landing_page_settings'))

@bp.route('/landing-page/features/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_landing_feature(id):
    """Deletar feature da landing page"""
    feature = LandingPageFeature.query.get_or_404(id)
    db.session.delete(feature)
    db.session.commit()
    
    flash('Feature excluída com sucesso!', 'success')
    return redirect(url_for('admin.landing_page_settings'))


# ============================================================================
# GESTÃO DE AVISOS E ANÚNCIOS
# ============================================================================

@bp.route('/landing-page/announcements')
@login_required
@admin_required
def announcements():
    """Gerenciar avisos e anúncios públicos"""
    from app.models import PublicAnnouncement
    
    filter_type = request.args.get('type', 'all')
    filter_status = request.args.get('status', 'all')
    
    query = PublicAnnouncement.query
    
    if filter_type != 'all':
        query = query.filter_by(announcement_type=filter_type)
    
    if filter_status == 'active':
        query = query.filter_by(is_active=True)
    elif filter_status == 'inactive':
        query = query.filter_by(is_active=False)
    
    announcements = query.order_by(
        PublicAnnouncement.priority.desc(),
        PublicAnnouncement.created_at.desc()
    ).all()
    
    return render_template('admin/announcements.html', announcements=announcements)


@bp.route('/landing-page/announcements/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    """Criar novo aviso/anúncio"""
    from app.models import PublicAnnouncement
    
    if request.method == 'POST':
        announcement = PublicAnnouncement(
            title=request.form.get('title'),
            content=request.form.get('content'),
            announcement_type=request.form.get('announcement_type', 'info'),
            icon=request.form.get('icon'),
            priority=request.form.get('priority', type=int, default=0),
            is_active=request.form.get('is_active') == 'on',
            show_on_homepage=request.form.get('show_on_homepage') == 'on',
            created_by=current_user.id
        )
        
        valid_until = request.form.get('valid_until')
        if valid_until:
            announcement.valid_until = datetime.strptime(valid_until, '%Y-%m-%dT%H:%M')
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Anúncio criado com sucesso!', 'success')
        return redirect(url_for('admin.announcements'))
    
    return render_template('admin/create_announcement.html')


@bp.route('/landing-page/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(id):
    """Editar aviso/anúncio"""
    from app.models import PublicAnnouncement
    
    announcement = PublicAnnouncement.query.get_or_404(id)
    
    if request.method == 'POST':
        announcement.title = request.form.get('title')
        announcement.content = request.form.get('content')
        announcement.announcement_type = request.form.get('announcement_type')
        announcement.icon = request.form.get('icon')
        announcement.priority = request.form.get('priority', type=int)
        announcement.is_active = request.form.get('is_active') == 'on'
        announcement.show_on_homepage = request.form.get('show_on_homepage') == 'on'
        
        valid_until = request.form.get('valid_until')
        if valid_until:
            announcement.valid_until = datetime.strptime(valid_until, '%Y-%m-%dT%H:%M')
        else:
            announcement.valid_until = None
        
        db.session.commit()
        
        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('admin.announcements'))
    
    return render_template('admin/edit_announcement.html', announcement=announcement)


@bp.route('/landing-page/announcements/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(id):
    """Deletar anúncio"""
    from app.models import PublicAnnouncement
    
    announcement = PublicAnnouncement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    
    flash('Anúncio excluído com sucesso!', 'success')
    return redirect(url_for('admin.announcements'))


# ============================================================================
# GESTÃO DE DEPOIMENTOS
# ============================================================================

@bp.route('/landing-page/testimonials')
@login_required
@admin_required
def testimonials():
    """Gerenciar depoimentos"""
    from app.models import LandingPageTestimonial
    
    testimonials = LandingPageTestimonial.query.order_by(
        LandingPageTestimonial.display_order
    ).all()
    
    return render_template('admin/testimonials.html', testimonials=testimonials)


@bp.route('/landing-page/testimonials/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_testimonial():
    """Criar depoimento"""
    from app.models import LandingPageTestimonial
    
    if request.method == 'POST':
        testimonial = LandingPageTestimonial(
            student_name=request.form.get('student_name'),
            instrument=request.form.get('instrument'),
            testimonial=request.form.get('testimonial'),
            rating=request.form.get('rating', type=int, default=5),
            display_order=request.form.get('display_order', type=int, default=0),
            is_active=request.form.get('is_active') == 'on',
            approved_by=current_user.id
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        flash('Depoimento criado com sucesso!', 'success')
        return redirect(url_for('admin.testimonials'))
    
    return render_template('admin/create_testimonial.html')


@bp.route('/landing-page/testimonials/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_testimonial(id):
    """Deletar depoimento"""
    from app.models import LandingPageTestimonial
    
    testimonial = LandingPageTestimonial.query.get_or_404(id)
    db.session.delete(testimonial)
    db.session.commit()
    
    flash('Depoimento excluído com sucesso!', 'success')
    return redirect(url_for('admin.testimonials'))


# ============================================================================
# GESTÃO DE GALERIA
# ============================================================================

@bp.route('/landing-page/gallery')
@login_required
@admin_required
def gallery():
    """Gerenciar galeria de fotos"""
    from app.models import LandingPageGallery
    
    category = request.args.get('category', 'all')
    
    query = LandingPageGallery.query
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    images = query.order_by(LandingPageGallery.display_order).all()
    
    return render_template('admin/gallery.html', images=images, category=category)


@bp.route('/landing-page/gallery/upload', methods=['POST'])
@login_required
@admin_required
def upload_gallery_image():
    """Upload de imagem para galeria"""
    from app.models import LandingPageGallery
    
    image = LandingPageGallery(
        title=request.form.get('title'),
        description=request.form.get('description'),
        image_url=request.form.get('image_url'),  # URL da imagem
        category=request.form.get('category', 'event'),
        is_featured=request.form.get('is_featured') == 'on',
        is_active=True,
        display_order=request.form.get('display_order', type=int, default=0),
        uploaded_by=current_user.id
    )
    
    db.session.add(image)
    db.session.commit()
    
    flash('Imagem adicionada à galeria!', 'success')
    return redirect(url_for('admin.gallery'))


@bp.route('/landing-page/gallery/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_gallery_image(id):
    """Deletar imagem da galeria"""
    from app.models import LandingPageGallery
    
    image = LandingPageGallery.query.get_or_404(id)
    db.session.delete(image)
    db.session.commit()
    
    flash('Imagem excluída da galeria!', 'success')
    return redirect(url_for('admin.gallery'))


# ============================================================================
# ROTAS DE ANALYTICS E CONFLITOS
# ============================================================================

@bp.route('/analytics/conflicts')
@login_required
@admin_required
def view_conflicts():
    """Visualização detalhada de conflitos"""
    conflicts = AnalyticsService.get_schedule_conflicts()
    
    return render_template('admin/conflicts.html', conflicts=conflicts)

@bp.route('/analytics/room-occupancy')
@login_required
@admin_required
def room_occupancy():
    """Análise de ocupação de salas"""
    days = request.args.get('days', 7, type=int)
    occupancy_data = AnalyticsService.get_room_occupancy(days=days)
    
    return render_template('admin/room_occupancy.html',
                         occupancy_data=occupancy_data,
                         days=days)

@bp.route('/analytics/api/revenue-chart')
@login_required
@admin_required
def api_revenue_chart():
    """API para dados do gráfico de receita"""
    months = request.args.get('months', 6, type=int)
    data = AnalyticsService.get_revenue_chart(months=months)
    return jsonify(data)

@bp.route('/analytics/api/students-chart')
@login_required
@admin_required
def api_students_chart():
    """API para dados do gráfico de alunos por instrumento"""
    data = AnalyticsService.get_students_by_instrument()
    return jsonify(data)

@bp.route('/analytics/api/attendance-chart')
@login_required
@admin_required
def api_attendance_chart():
    """API para dados do gráfico de frequência"""
    months = request.args.get('months', 6, type=int)
    data = AnalyticsService.get_attendance_rate_chart(months=months)
    return jsonify(data)
