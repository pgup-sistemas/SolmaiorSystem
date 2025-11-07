
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Student, Enrollment, Payment, User, Discount, FrequencyDiscount, LessonSchedule
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, and_, or_
import io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover
    REPORTLAB_AVAILABLE = False
    A4 = colors = getSampleStyleSheet = ParagraphStyle = mm = SimpleDocTemplate = Table = TableStyle = Paragraph = Spacer = None

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

    if not REPORTLAB_AVAILABLE:
        flash('Geração de recibo indisponível. Instale o pacote "reportlab" no ambiente para habilitar o PDF.', 'error')
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
    )

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


@bp.route('/discounts')
@login_required
@financial_required
def discounts():
    """Lista de descontos configurados"""
    discounts = Discount.query.order_by(Discount.created_at.desc()).all()
    return render_template('financial/discounts.html', discounts=discounts)


@bp.route('/discounts/create', methods=['GET', 'POST'])
@login_required
@financial_required
def create_discount():
    """Criar novo desconto"""
    if request.method == 'POST':
        try:
            discount = Discount(
                name=request.form.get('name'),
                description=request.form.get('description'),
                discount_type=request.form.get('discount_type'),
                discount_value=float(request.form.get('discount_value')),
                condition_type=request.form.get('condition_type'),
                condition_value=float(request.form.get('condition_value')) if request.form.get('condition_value') else None,
                valid_from=datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d').date() if request.form.get('valid_from') else None,
                valid_until=datetime.strptime(request.form.get('valid_until'), '%Y-%m-%d').date() if request.form.get('valid_until') else None,
                auto_apply=request.form.get('auto_apply') == 'on',
                is_active=True,
                created_by=current_user.id
            )
            
            db.session.add(discount)
            db.session.commit()
            
            flash('Desconto criado com sucesso!', 'success')
            return redirect(url_for('financial.discounts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar desconto: {str(e)}', 'error')
    
    return render_template('financial/create_discount.html')


@bp.route('/discounts/<int:discount_id>/toggle', methods=['POST'])
@login_required
@financial_required
def toggle_discount(discount_id):
    """Ativar/desativar desconto"""
    discount = Discount.query.get_or_404(discount_id)
    
    try:
        discount.is_active = not discount.is_active
        db.session.commit()
        
        status = 'ativado' if discount.is_active else 'desativado'
        flash(f'Desconto {status} com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar desconto: {str(e)}', 'error')
    
    return redirect(url_for('financial.discounts'))


@bp.route('/payments/<int:payment_id>/apply-discount', methods=['POST'])
@login_required
@financial_required
def apply_discount(payment_id):
    """Aplicar desconto manual a um pagamento"""
    payment = Payment.query.get_or_404(payment_id)
    
    try:
        discount_type = request.form.get('discount_type')
        discount_value = float(request.form.get('discount_value'))
        discount_reason = request.form.get('discount_reason')
        
        if discount_type == 'percentage':
            payment.discount = payment.amount * (discount_value / 100)
        else:  # fixed_amount
            payment.discount = discount_value
        
        payment.discount_reason = discount_reason
        payment.total_amount = payment.amount - payment.discount + payment.late_fee
        
        db.session.commit()
        flash('Desconto aplicado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aplicar desconto: {str(e)}', 'error')
    
    return redirect(url_for('financial.payments'))


@bp.route('/payments/<int:payment_id>/installments', methods=['POST'])
@login_required
@financial_required
def create_installments(payment_id):
    """Criar parcelamento de um pagamento"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'pending':
        flash('Apenas pagamentos pendentes podem ser parcelados.', 'error')
        return redirect(url_for('financial.payments'))
    
    try:
        num_installments = int(request.form.get('num_installments'))
        
        if num_installments < 2 or num_installments > 12:
            flash('Número de parcelas deve estar entre 2 e 12.', 'error')
            return redirect(url_for('financial.payments'))
        
        # Calcular valor de cada parcela
        installment_amount = payment.total_amount / num_installments
        
        # Atualizar pagamento original
        payment.is_installment = True
        payment.installment_number = 1
        payment.installment_total = num_installments
        payment.amount = installment_amount
        payment.total_amount = installment_amount
        
        # Criar parcelas restantes
        for i in range(2, num_installments + 1):
            due_date = payment.due_date + relativedelta(months=i-1)
            
            installment = Payment(
                enrollment_id=payment.enrollment_id,
                reference_month=payment.reference_month,
                due_date=due_date,
                amount=installment_amount,
                total_amount=installment_amount,
                is_installment=True,
                installment_number=i,
                installment_total=num_installments,
                parent_payment_id=payment.id,
                status='pending'
            )
            db.session.add(installment)
        
        db.session.commit()
        flash(f'Pagamento parcelado em {num_installments}x com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar parcelamento: {str(e)}', 'error')
    
    return redirect(url_for('financial.payments'))


@bp.route('/frequency-discounts')
@login_required
@financial_required
def frequency_discounts():
    """Relatório de descontos por frequência"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calcular descontos automáticos por frequência
    calculate_frequency_discounts(current_month, current_year)
    
    discounts = FrequencyDiscount.query.filter(
        FrequencyDiscount.month == current_month,
        FrequencyDiscount.year == current_year
    ).all()
    
    return render_template('financial/frequency_discounts.html', discounts=discounts)


@bp.route('/frequency-discounts/<int:discount_id>/apply', methods=['POST'])
@login_required
@financial_required
def apply_frequency_discount(discount_id):
    """Aplicar desconto por frequência ao pagamento do mês"""
    freq_discount = FrequencyDiscount.query.get_or_404(discount_id)
    
    if freq_discount.applied:
        flash('Este desconto já foi aplicado.', 'warning')
        return redirect(url_for('financial.frequency_discounts'))
    
    try:
        # Buscar pagamento do mês correspondente
        payment = Payment.query.join(Enrollment).filter(
            Enrollment.student_id == freq_discount.student_id,
            Payment.reference_month >= datetime(freq_discount.year, freq_discount.month, 1).date(),
            Payment.reference_month < datetime(freq_discount.year, freq_discount.month, 1).date() + relativedelta(months=1),
            Payment.status == 'pending'
        ).first()
        
        if not payment:
            flash('Pagamento correspondente não encontrado.', 'error')
            return redirect(url_for('financial.frequency_discounts'))
        
        # Aplicar desconto
        discount_amount = payment.amount * (freq_discount.discount_percentage / 100)
        payment.discount = discount_amount
        payment.discount_reason = freq_discount.reason
        payment.total_amount = payment.amount - payment.discount + payment.late_fee
        
        freq_discount.applied = True
        
        db.session.commit()
        flash('Desconto por frequência aplicado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aplicar desconto: {str(e)}', 'error')
    
    return redirect(url_for('financial.frequency_discounts'))


def calculate_frequency_discounts(month, year):
    """Calcular descontos automáticos por frequência para o mês"""
    # Buscar todos os alunos ativos
    students = Student.query.filter_by(is_active=True).all()
    
    for student in students:
        # Verificar se já existe desconto calculado
        existing = FrequencyDiscount.query.filter_by(
            student_id=student.id,
            month=month,
            year=year
        ).first()
        
        if existing:
            continue
        
        # Calcular taxa de frequência do mês anterior
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        
        total_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student.id,
            func.extract('month', LessonSchedule.lesson_date) == prev_month,
            func.extract('year', LessonSchedule.lesson_date) == prev_year,
            LessonSchedule.status.in_(['completed', 'absent'])
        ).count()
        
        if total_lessons == 0:
            continue
        
        present_lessons = LessonSchedule.query.filter(
            LessonSchedule.student_id == student.id,
            func.extract('month', LessonSchedule.lesson_date) == prev_month,
            func.extract('year', LessonSchedule.lesson_date) == prev_year,
            LessonSchedule.attendance_status == 'present'
        ).count()
        
        attendance_rate = (present_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Definir desconto baseado na frequência
        discount_percentage = 0
        reason = ''
        
        if attendance_rate == 100:
            discount_percentage = 10
            reason = 'Frequência 100%'
        elif attendance_rate >= 95:
            discount_percentage = 5
            reason = 'Frequência >= 95%'
        elif attendance_rate >= 90:
            discount_percentage = 3
            reason = 'Frequência >= 90%'
        
        if discount_percentage > 0:
            freq_discount = FrequencyDiscount(
                student_id=student.id,
                month=month,
                year=year,
                attendance_rate=round(attendance_rate, 2),
                discount_percentage=discount_percentage,
                reason=reason,
                applied=False
            )
            db.session.add(freq_discount)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao calcular descontos por frequência: {str(e)}')
