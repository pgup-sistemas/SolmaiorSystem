from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models import NewsPost, TrialLesson

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    news = NewsPost.query.filter_by(is_published=True).order_by(NewsPost.published_at.desc()).limit(3).all()
    return render_template('public/index.html', news=news)

@bp.route('/about')
def about():
    return render_template('public/about.html')

@bp.route('/trial-lesson', methods=['GET', 'POST'])
def trial_lesson():
    if request.method == 'POST':
        trial = TrialLesson(
            full_name=request.form.get('full_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            instrument=request.form.get('instrument'),
            message=request.form.get('message')
        )
        
        db.session.add(trial)
        db.session.commit()
        
        flash('Solicitação enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('public.index'))
    
    return render_template('public/trial_lesson.html')

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
