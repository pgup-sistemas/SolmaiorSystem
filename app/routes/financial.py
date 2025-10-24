
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Student, Enrollment, Payment, User
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

bp = Blueprint('financial', __name__, url_prefix='/financial')

def financial_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'secretary']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@financial_required
def dashboard():
    total_active_enrollments = Enrollment.query.filter_by(status='active').count()
    
    pending_payments = Payment.query.filter_by(status='pending').count()
    overdue_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.now().date()
    ).count()
    
    current_month_revenue = db.session.query(db.func.sum(Payment.total_amount)).filter(
        Payment.status == 'paid',
        db.func.extract('month', Payment.payment_date) == datetime.now().month,
        db.func.extract('year', Payment.payment_date) == datetime.now().year
    ).scalar() or 0
    
    recent_payments = Payment.query.filter_by(status='paid').order_by(Payment.payment_date.desc()).limit(10).all()
    
    return render_template('financial/dashboard.html',
                         total_active_enrollments=total_active_enrollments,
                         pending_payments=pending_payments,
                         overdue_payments=overdue_payments,
                         current_month_revenue=current_month_revenue,
                         recent_payments=recent_payments)

@bp.route('/enrollments')
@login_required
@financial_required
def enrollments():
    enrollments = Enrollment.query.order_by(Enrollment.created_at.desc()).all()
    return render_template('financial/enrollments.html', enrollments=enrollments)

@bp.route('/enrollments/create', methods=['GET', 'POST'])
@login_required
@financial_required
def create_enrollment():
    if request.method == 'POST':
        try:
            enrollment = Enrollment(
                student_id=request.form.get('student_id', type=int),
                plan_type=request.form.get('plan_type'),
                monthly_value=request.form.get('monthly_value', type=float),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None,
                status='active'
            )
            
            db.session.add(enrollment)
            db.session.flush()
            
            # Gerar mensalidades automáticas
            generate_monthly_payments(enrollment)
            
            db.session.commit()
            flash('Matrícula criada com sucesso!', 'success')
            return redirect(url_for('financial.enrollments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar matrícula: {str(e)}', 'error')
            return redirect(url_for('financial.create_enrollment'))
    
    students = Student.query.all()
    return render_template('financial/create_enrollment.html', students=students)

@bp.route('/payments')
@login_required
@financial_required
def payments():
    status_filter = request.args.get('status', 'all')
    
    query = Payment.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    payments = query.order_by(Payment.due_date.desc()).all()
    return render_template('financial/payments.html', payments=payments, status_filter=status_filter)

@bp.route('/payments/<int:payment_id>/register', methods=['POST'])
@login_required
@financial_required
def register_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    try:
        payment.payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        payment.payment_method = request.form.get('payment_method')
        payment.status = 'paid'
        
        # Calcular multa por atraso
        if payment.payment_date > payment.due_date:
            days_late = (payment.payment_date - payment.due_date).days
            payment.late_fee = payment.amount * 0.02 + (payment.amount * 0.001 * days_late)
        
        payment.total_amount = payment.amount - payment.discount + payment.late_fee
        payment.receipt_number = f'REC{datetime.now().year}{payment.id:06d}'
        payment.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Pagamento registrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar pagamento: {str(e)}', 'error')
    
    return redirect(url_for('financial.payments'))

@bp.route('/payments/<int:payment_id>/receipt')
@login_required
@financial_required
def generate_receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'paid':
        flash('Este pagamento ainda não foi realizado.', 'error')
        return redirect(url_for('financial.payments'))
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1e40af'), alignment=1)
    elements.append(Paragraph('ESCOLA DE MÚSICA SOLMAIOR', title_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('RECIBO DE PAGAMENTO', title_style))
    elements.append(Spacer(1, 20))
    
    # Informações do recibo
    info_data = [
        ['Recibo Nº:', payment.receipt_number or f'REC-{payment.id:05d}'],
        ['Data de Pagamento:', payment.payment_date.strftime('%d/%m/%Y')],
        ['Aluno:', payment.enrollment.student.user.full_name],
        ['Referência:', payment.reference_month.strftime('%m/%Y')],
        ['Valor:', f'R$ {payment.amount:.2f}'],
        ['Desconto:', f'R$ {payment.discount:.2f}'],
        ['Multa/Juros:', f'R$ {payment.late_fee:.2f}'],
        ['Total Pago:', f'R$ {payment.total_amount:.2f}'],
        ['Forma de Pagamento:', payment.payment_method or 'Não especificado']
    ]
    
    table = Table(info_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Observações
    if payment.notes:
        obs_style = ParagraphStyle('Obs', parent=styles['Normal'], fontSize=9)
        elements.append(Paragraph(f'<b>Observações:</b> {payment.notes}', obs_style))
        elements.append(Spacer(1, 20))
    
    # Assinatura
    elements.append(Spacer(1, 40))
    signature_data = [
        ['_' * 50],
        ['Assinatura do Responsável']
    ]
    signature_table = Table(signature_data, colWidths=[450])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))
    elements.append(signature_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'recibo_{payment.receipt_number or payment.id}.pdf'
    )ors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Assinatura
    elements.append(Paragraph('_______________________________________', styles['Normal']))
    elements.append(Paragraph('Escola de Música Sol Maior', styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'recibo_{payment.receipt_number}.pdf', mimetype='application/pdf')

@bp.route('/reports/overdue')
@login_required
@financial_required
def overdue_report():
    overdue_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.now().date()
    ).order_by(Payment.due_date).all()
    
    return render_template('financial/overdue_report.html', overdue_payments=overdue_payments)

def generate_monthly_payments(enrollment):
    """Gera mensalidades automáticas para uma matrícula"""
    start_date = enrollment.start_date
    end_date = enrollment.end_date or (start_date + relativedelta(months=12))
    
    current_date = start_date
    while current_date <= end_date:
        due_date = current_date.replace(day=10)
        
        payment = Payment(
            enrollment_id=enrollment.id,
            reference_month=current_date,
            due_date=due_date,
            amount=enrollment.monthly_value,
            total_amount=enrollment.monthly_value,
            status='pending'
        )
        
        db.session.add(payment)
        current_date += relativedelta(months=1)
