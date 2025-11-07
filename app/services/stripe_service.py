import os
import stripe
from datetime import datetime
from flask import current_app, url_for
from app import db
from app.models import Payment, Student, User

class StripeService:
    def __init__(self):
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        self.public_key = os.environ.get('STRIPE_PUBLIC_KEY')
    
    def get_or_create_customer(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            raise ValueError(f"Student with id {student_id} not found")
        
        user = student.user
        
        if student.stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(student.stripe_customer_id)
                return customer
            except stripe.error.InvalidRequestError:
                pass
        
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            phone=user.phone or '',
            metadata={
                'student_id': student.id,
                'user_id': user.id
            }
        )
        
        student.stripe_customer_id = customer.id
        db.session.commit()
        
        return customer
    
    def create_payment_intent(self, payment_id, return_url=None):
        payment = Payment.query.get(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")
        
        student = payment.enrollment.student
        customer = self.get_or_create_customer(student.id)
        
        amount_cents = int(payment.total_amount * 100)
        
        if payment.stripe_payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                if intent.status not in ['succeeded', 'canceled']:
                    return intent
            except stripe.error.InvalidRequestError:
                pass
        
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='brl',
            customer=customer.id,
            metadata={
                'payment_id': payment.id,
                'enrollment_id': payment.enrollment_id,
                'student_id': student.id,
                'reference_month': payment.reference_month.strftime('%Y-%m')
            },
            description=f"Mensalidade - {payment.reference_month.strftime('%m/%Y')} - {student.user.full_name}",
            automatic_payment_methods={'enabled': True},
        )
        
        payment.stripe_payment_intent_id = intent.id
        payment.stripe_client_secret = intent.client_secret
        payment.stripe_customer_id = customer.id
        payment.stripe_status = intent.status
        db.session.commit()
        
        return intent
    
    def create_checkout_session(self, payment_id, success_url=None, cancel_url=None):
        payment = Payment.query.get(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")
        
        student = payment.enrollment.student
        customer = self.get_or_create_customer(student.id)
        
        domain = self._get_domain()
        
        if not success_url:
            success_url = f"https://{domain}/student/payment/success?payment_id={payment_id}"
        if not cancel_url:
            cancel_url = f"https://{domain}/student/payment/cancel?payment_id={payment_id}"
        
        amount_cents = int(payment.total_amount * 100)
        
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': f"Mensalidade - {payment.reference_month.strftime('%m/%Y')}",
                        'description': f"Pagamento de mensalidade referente a {payment.reference_month.strftime('%B %Y')}",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'payment_id': payment.id,
                'enrollment_id': payment.enrollment_id,
                'student_id': student.id,
            }
        )
        
        payment.stripe_payment_intent_id = session.payment_intent if session.payment_intent else session.id
        payment.stripe_status = 'checkout_created'
        db.session.commit()
        
        return session
    
    def handle_webhook(self, payload, sig_header):
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_success(payment_intent)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failed(payment_intent)
        
        elif event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_completed(session)
        
        return event
    
    def _handle_payment_success(self, payment_intent):
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if not payment_id:
            return
        
        payment = Payment.query.get(int(payment_id))
        if not payment:
            return
        
        payment.status = 'paid'
        payment.payment_date = datetime.utcnow().date()
        payment.stripe_payment_intent_id = payment_intent['id']
        payment.stripe_charge_id = payment_intent.get('latest_charge')
        payment.stripe_status = payment_intent['status']
        payment.stripe_webhook_received = True
        payment.payment_method = 'credit_card'
        
        db.session.commit()
    
    def _handle_payment_failed(self, payment_intent):
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if not payment_id:
            return
        
        payment = Payment.query.get(int(payment_id))
        if not payment:
            return
        
        payment.stripe_status = payment_intent['status']
        payment.stripe_error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
        payment.stripe_webhook_received = True
        
        db.session.commit()
    
    def _handle_checkout_completed(self, session):
        payment_id = session.get('metadata', {}).get('payment_id')
        if not payment_id:
            return
        
        payment = Payment.query.get(int(payment_id))
        if not payment:
            return
        
        payment.status = 'paid'
        payment.payment_date = datetime.utcnow().date()
        payment.stripe_payment_intent_id = session.get('payment_intent')
        payment.stripe_status = session['payment_status']
        payment.stripe_webhook_received = True
        payment.payment_method = 'credit_card'
        
        db.session.commit()
    
    def _get_domain(self):
        if os.environ.get('REPLIT_DEPLOYMENT'):
            return os.environ.get('REPLIT_DEV_DOMAIN')
        domains = os.environ.get('REPLIT_DOMAINS', '')
        if domains:
            return domains.split(',')[0]
        return 'localhost:5000'
    
    def get_payment_status(self, payment_id):
        payment = Payment.query.get(payment_id)
        if not payment or not payment.stripe_payment_intent_id:
            return None
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            return intent.status
        except stripe.error.InvalidRequestError:
            return None
    
    def cancel_payment_intent(self, payment_id):
        payment = Payment.query.get(payment_id)
        if not payment or not payment.stripe_payment_intent_id:
            return False
        
        try:
            intent = stripe.PaymentIntent.cancel(payment.stripe_payment_intent_id)
            payment.status = 'cancelled'
            payment.stripe_status = intent.status
            db.session.commit()
            return True
        except stripe.error.InvalidRequestError:
            return False
