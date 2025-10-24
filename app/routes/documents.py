
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Document, Student, Teacher
from datetime import datetime
import os

bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'mp3', 'wav', 'mp4', 'avi'}
UPLOAD_FOLDER = 'app/static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in {'pdf', 'doc', 'docx', 'txt'}:
        return 'document'
    elif ext in {'jpg', 'jpeg', 'png'}:
        return 'image'
    elif ext in {'mp3', 'wav'}:
        return 'audio'
    elif ext in {'mp4', 'avi'}:
        return 'video'
    return 'other'

@bp.route('/')
@login_required
def index():
    if current_user.role == 'student':
        documents = Document.query.filter(
            db.or_(
                Document.is_public == True,
                Document.related_student_id == current_user.student_profile.id
            )
        ).order_by(Document.created_at.desc()).all()
    elif current_user.role == 'teacher':
        documents = Document.query.filter(
            db.or_(
                Document.is_public == True,
                Document.related_teacher_id == current_user.teacher_profile.id
            )
        ).order_by(Document.created_at.desc()).all()
    else:
        documents = Document.query.order_by(Document.created_at.desc()).all()
    
    return render_template('documents/index.html', documents=documents)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                
                # Criar diretório se não existir
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                
                document = Document(
                    title=request.form.get('title'),
                    description=request.form.get('description'),
                    file_name=filename,
                    file_path=file_path,
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    file_size=os.path.getsize(file_path),
                    category=request.form.get('category'),
                    uploaded_by=current_user.id,
                    related_student_id=request.form.get('related_student_id', type=int) if request.form.get('related_student_id') else None,
                    related_teacher_id=request.form.get('related_teacher_id', type=int) if request.form.get('related_teacher_id') else None,
                    is_public=request.form.get('is_public') == 'on'
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Documento enviado com sucesso!', 'success')
                return redirect(url_for('documents.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao enviar documento: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Tipo de arquivo não permitido.', 'error')
            return redirect(request.url)
    
    students = Student.query.all() if current_user.role in ['admin', 'secretary'] else []
    teachers = Teacher.query.all() if current_user.role in ['admin', 'secretary'] else []
    
    return render_template('documents/upload.html', students=students, teachers=teachers)

@bp.route('/download/<int:document_id>')
@login_required
def download(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Verificar permissões
    if not document.is_public:
        if current_user.role == 'student' and document.related_student_id != current_user.student_profile.id:
            flash('Você não tem permissão para acessar este documento.', 'error')
            return redirect(url_for('documents.index'))
        elif current_user.role == 'teacher' and document.related_teacher_id != current_user.teacher_profile.id:
            flash('Você não tem permissão para acessar este documento.', 'error')
            return redirect(url_for('documents.index'))
    
    directory = os.path.dirname(document.file_path)
    filename = os.path.basename(document.file_path)
    
    return send_from_directory(directory, filename, as_attachment=True, download_name=document.file_name)

@bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete(document_id):
    document = Document.query.get_or_404(document_id)
    
    if current_user.role not in ['admin', 'secretary'] and document.uploaded_by != current_user.id:
        flash('Você não tem permissão para deletar este documento.', 'error')
        return redirect(url_for('documents.index'))
    
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        db.session.delete(document)
        db.session.commit()
        
        flash('Documento deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar documento: {str(e)}', 'error')
    
    return redirect(url_for('documents.index'))
