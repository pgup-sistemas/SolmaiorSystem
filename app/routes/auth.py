from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Student, Teacher

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Sua conta está inativa. Entre em contato com a administração.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=request.form.get('remember', False))
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'secretary':
                return redirect(url_for('secretary.dashboard'))
            else:
                return redirect(url_for('public.index'))
        else:
            flash('Email ou senha inválidos.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('public.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        if not email or not password or not full_name:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está registrado.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role='student'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()
            
            student = Student(
                user_id=user.id,
                instrument='Não especificado',
                level='Iniciante'
            )
            db.session.add(student)
            
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar cadastro: {str(e)}', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Aqui você pode implementar o envio de email
            # Por enquanto, vamos apenas mostrar uma mensagem
            flash('Se este email estiver cadastrado, você receberá instruções para recuperar sua senha.', 'success')
        else:
            flash('Se este email estiver cadastrado, você receberá instruções para recuperar sua senha.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')
