import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Payment, Enrollment, Student
from app.services.stripe_service import StripeService

bp = Blueprint('payments', __name__, url_prefix='/payments')

def student_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['student', 'admin', 'secretary']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/payment/<int:payment_id>')
@login_required
@student_or_admin_required
def payment_detail(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == 'student':
        if payment.enrollment.student.user_id != current_user.id:
            flash('Você não tem permissão para acessar este pagamento.', 'error')
            return redirect(url_for('student.dashboard'))
    
    stripe_service = StripeService()
    
    return render_template('payments/detail.html',
                         payment=payment,
                         stripe_public_key=stripe_service.public_key)

@bp.route('/payment/<int:payment_id>/checkout', methods=['POST'])
@login_required
@student_or_admin_required
def create_checkout(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == 'student':
        if payment.enrollment.student.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    if payment.status == 'paid':
        return jsonify({'error': 'Payment already paid'}), 400
    
    try:
        stripe_service = StripeService()
        session = stripe_service.create_checkout_session(payment_id)
        
        return jsonify({
            'sessionId': session.id,
            'url': session.url
        })
    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/payment/<int:payment_id>/payment-intent', methods=['POST'])
@login_required
@student_or_admin_required
def create_payment_intent(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == 'student':
        if payment.enrollment.student.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    if payment.status == 'paid':
        return jsonify({'error': 'Payment already paid'}), 400
    
    try:
        stripe_service = StripeService()
        intent = stripe_service.create_payment_intent(payment_id)
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id
        })
    except Exception as e:
        current_app.logger.error(f"Error creating payment intent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/payment/<int:payment_id>/status')
@login_required
@student_or_admin_required
def payment_status(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == 'student':
        if payment.enrollment.student.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    stripe_service = StripeService()
    status = stripe_service.get_payment_status(payment_id)
    
    return jsonify({
        'id': payment.id,
        'status': payment.status,
        'stripe_status': status or payment.stripe_status,
        'amount': payment.total_amount,
        'paid_date': payment.payment_date.isoformat() if payment.payment_date else None
    })

@bp.route('/payment/<int:payment_id>/cancel', methods=['POST'])
@login_required
@student_or_admin_required
def cancel_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role not in ['admin', 'secretary']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        stripe_service = StripeService()
        success = stripe_service.cancel_payment_intent(payment_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Payment cancelled successfully'})
        else:
            return jsonify({'error': 'Could not cancel payment'}), 400
    except Exception as e:
        current_app.logger.error(f"Error cancelling payment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        stripe_service = StripeService()
        event = stripe_service.handle_webhook(payload, sig_header)
        
        current_app.logger.info(f"Stripe webhook received: {event['type']}")
        
        return jsonify({'success': True}), 200
    except ValueError as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected webhook error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/success')
@login_required
def payment_success():
    payment_id = request.args.get('payment_id', type=int)
    
    if payment_id:
        payment = Payment.query.get(payment_id)
        if payment and current_user.role == 'student':
            if payment.enrollment.student.user_id != current_user.id:
                flash('Acesso não autorizado.', 'error')
                return redirect(url_for('student.dashboard'))
        
        return render_template('payments/success.html', payment=payment)
    
    return render_template('payments/success.html')

@bp.route('/cancel')
@login_required
def payment_cancel():
    payment_id = request.args.get('payment_id', type=int)
    
    if payment_id:
        payment = Payment.query.get(payment_id)
        if payment and current_user.role == 'student':
            if payment.enrollment.student.user_id != current_user.id:
                flash('Acesso não autorizado.', 'error')
                return redirect(url_for('student.dashboard'))
        
        return render_template('payments/cancel.html', payment=payment)
    
    return render_template('payments/cancel.html')
