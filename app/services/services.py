# ============================================================================
# PAYMENT GATEWAY INTEGRATIONS
# ============================================================================

import requests
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from app import db
from app.models import Payment, Enrollment, Student, FinancialAuditLog


class PaymentGatewayService:
    """Serviço base para integrações com gateways de pagamento"""

    def __init__(self, gateway_name):
        self.gateway_name = gateway_name
        self.config = self._load_config()

    def _load_config(self):
        """Carregar configurações do gateway"""
        # TODO: Implementar carregamento de configurações seguras
        return {
            'api_key': 'your_api_key',
            'api_secret': 'your_api_secret',
            'webhook_secret': 'your_webhook_secret',
            'sandbox': True
        }

    def create_payment(self, payment, return_url=None, cancel_url=None):
        """Criar pagamento no gateway"""
        raise NotImplementedError

    def check_payment_status(self, gateway_payment_id):
        """Verificar status do pagamento"""
        raise NotImplementedError

    def process_webhook(self, webhook_data):
        """Processar webhook do gateway"""
        raise NotImplementedError


class MercadoPagoService(PaymentGatewayService):
    """Integração com Mercado Pago"""

    def __init__(self):
        super().__init__('mercado_pago')
        self.base_url = 'https://api.mercadopago.com' if not self.config.get('sandbox') else 'https://api.mercadopago.com'

    def create_payment(self, payment, return_url=None, cancel_url=None):
        """Criar pagamento no Mercado Pago"""

        student = payment.enrollment.student

        payment_data = {
            "transaction_amount": float(payment.total_amount),
            "description": f"Mensalidade {payment.reference_month.strftime('%m/%Y')} - {student.user.full_name}",
            "payment_method_id": "pix",  # ou outros métodos
            "payer": {
                "email": student.user.email,
                "first_name": student.user.full_name.split()[0],
                "last_name": " ".join(student.user.full_name.split()[1:]) if len(student.user.full_name.split()) > 1 else "",
                "identification": {
                    "type": "CPF",
                    "number": student.cpf or "00000000000"
                }
            },
            "external_reference": f"payment_{payment.id}",
            "notification_url": f"{self.config.get('webhook_url')}/webhooks/mercadopago",
            "expires_in": 3600  # 1 hora
        }

        headers = {
            'Authorization': f'Bearer {self.config["access_token"]}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f'{self.base_url}/v1/payments',
                json=payment_data,
                headers=headers
            )

            if response.status_code == 201:
                result = response.json()
                payment.gateway_payment_id = str(result['id'])
                payment.gateway_name = 'mercado_pago'
                payment.gateway_data = json.dumps(result)

                # Se for PIX, salvar QR code
                if result.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code'):
                    payment.pix_qr_code = result['point_of_interaction']['transaction_data']['qr_code']

                db.session.commit()
                return {'success': True, 'payment_url': result.get('point_of_interaction', {}).get('transaction_data', {}).get('ticket_url')}

            return {'success': False, 'error': response.text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_payment_status(self, gateway_payment_id):
        """Verificar status no Mercado Pago"""

        headers = {
            'Authorization': f'Bearer {self.config["access_token"]}'
        }

        try:
            response = requests.get(
                f'{self.base_url}/v1/payments/{gateway_payment_id}',
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'status': result['status'],  # approved, pending, cancelled, etc.
                    'gateway_data': result
                }

            return {'status': 'error', 'error': response.text}

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def process_webhook(self, webhook_data):
        """Processar webhook do Mercado Pago"""

        # Verificar assinatura do webhook
        if not self._verify_webhook_signature(webhook_data):
            return {'success': False, 'error': 'Invalid signature'}

        # Processar diferentes tipos de eventos
        if webhook_data.get('type') == 'payment':
            payment_id = webhook_data['data']['id']
            gateway_result = self.check_payment_status(payment_id)

            if gateway_result['status'] == 'approved':
                # Atualizar pagamento local
                payment = Payment.query.filter_by(gateway_payment_id=str(payment_id)).first()
                if payment and payment.status == 'pending':
                    payment.status = 'paid'
                    payment.payment_date = datetime.utcnow()
                    payment.gateway_data = json.dumps(gateway_result['gateway_data'])

                    # Log da transação
                    FinancialService.log_financial_action(
                        1, 'payment_approved', 'Payment', payment.id,
                        {'status': 'pending'}, {'status': 'paid'},
                        f'Pagamento aprovado via {self.gateway_name}', None, None
                    )

                    db.session.commit()
                    return {'success': True, 'message': 'Payment approved'}

        return {'success': False, 'error': 'Unhandled webhook event'}

    def _verify_webhook_signature(self, webhook_data):
        """Verificar assinatura do webhook"""
        # Implementar verificação HMAC
        return True  # TODO: Implementar verificação real


class PagSeguroService(PaymentGatewayService):
    """Integração com PagSeguro"""

    def __init__(self):
        super().__init__('pagseguro')
        self.base_url = 'https://ws.pagseguro.uol.com.br' if not self.config.get('sandbox') else 'https://ws.sandbox.pagseguro.uol.com.br'

    def create_payment(self, payment, return_url=None, cancel_url=None):
        """Criar pagamento no PagSeguro"""

        student = payment.enrollment.student

        payment_data = {
            "email": self.config["email"],
            "token": self.config["token"],
            "currency": "BRL",
            "itemId1": f"payment_{payment.id}",
            "itemDescription1": f"Mensalidade {payment.reference_month.strftime('%m/%Y')}",
            "itemAmount1": f"{payment.total_amount:.2f}",
            "itemQuantity1": "1",
            "reference": f"payment_{payment.id}",
            "senderName": student.user.full_name,
            "senderEmail": student.user.email,
            "senderCPF": student.cpf or "00000000000",
            "redirectURL": return_url,
            "notificationURL": f"{self.config.get('webhook_url')}/webhooks/pagseguro"
        }

        try:
            response = requests.post(
                f'{self.base_url}/v2/checkout',
                data=payment_data
            )

            if response.status_code == 200:
                result = response.json() if response.headers.get('content-type') == 'application/json' else {'code': response.text.strip()}

                payment.gateway_payment_id = result.get('code')
                payment.gateway_name = 'pagseguro'
                payment.gateway_data = json.dumps(result)

                payment_url = f"https://pagseguro.uol.com.br/v2/checkout/payment.html?code={result.get('code')}"
                db.session.commit()

                return {'success': True, 'payment_url': payment_url}

            return {'success': False, 'error': response.text}

        except Exception as e:
            return {'success': False, 'error': str(e)}


class StripeService(PaymentGatewayService):
    """Integração com Stripe"""

    def __init__(self):
        super().__init__('stripe')
        self.base_url = 'https://api.stripe.com/v1'

    def create_payment(self, payment, return_url=None, cancel_url=None):
        """Criar pagamento no Stripe"""

        student = payment.enrollment.student

        payment_data = {
            'amount': int(payment.total_amount * 100),  # Stripe usa centavos
            'currency': 'brl',
            'description': f"Mensalidade {payment.reference_month.strftime('%m/%Y')} - {student.user.full_name}",
            'metadata': {
                'payment_id': payment.id,
                'student_id': student.id,
                'reference_month': payment.reference_month.strftime('%Y-%m')
            },
            'receipt_email': student.user.email
        }

        headers = {
            'Authorization': f'Bearer {self.config["secret_key"]}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            # Criar PaymentIntent
            response = requests.post(
                f'{self.base_url}/payment_intents',
                data=payment_data,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()

                payment.gateway_payment_id = result['id']
                payment.gateway_name = 'stripe'
                payment.gateway_data = json.dumps(result)

                db.session.commit()

                return {
                    'success': True,
                    'client_secret': result['client_secret'],
                    'payment_intent_id': result['id']
                }

            return {'success': False, 'error': response.text}

        except Exception as e:
            return {'success': False, 'error': str(e)}


class PaymentGatewayManager:
    """Gerenciador de gateways de pagamento"""

    def __init__(self):
        self.gateways = {
            'mercado_pago': MercadoPagoService(),
            'pagseguro': PagSeguroService(),
            'stripe': StripeService()
        }

    def get_gateway(self, gateway_name):
        """Retornar instância do gateway"""
        return self.gateways.get(gateway_name)

    def create_payment(self, payment, gateway_name='mercado_pago', **kwargs):
        """Criar pagamento usando gateway específico"""
        gateway = self.get_gateway(gateway_name)
        if not gateway:
            return {'success': False, 'error': f'Gateway {gateway_name} não encontrado'}

        return gateway.create_payment(payment, **kwargs)

    def process_webhook(self, gateway_name, webhook_data):
        """Processar webhook de um gateway específico"""
        gateway = self.get_gateway(gateway_name)
        if not gateway:
            return {'success': False, 'error': f'Gateway {gateway_name} não encontrado'}

        return gateway.process_webhook(webhook_data)

    def get_available_gateways(self):
        """Retornar lista de gateways disponíveis"""
        return list(self.gateways.keys())


# Instância global do gerenciador
payment_gateway_manager = PaymentGatewayManager()
