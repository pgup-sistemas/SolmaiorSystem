# ============================================================================
# SERVICES MODULE - Inicialização e imports
# ============================================================================

# Import existing services
from .analytics_service import AnalyticsService
from .recital_service import RecitalService
from .pdf_generator import RecitalPDFGenerator

# Import new services from services.py
try:
    from .services import (
        ScheduleService,
        WaitlistService,
        MakeupLessonService,
        FinancialService,
        NotificationService,
        PredictiveService,
        EnrollmentService,
        PaymentGatewayService,
        MercadoPagoService,
        PagSeguroService,
        StripeService,
        PaymentGatewayManager,
        payment_gateway_manager
    )
except ImportError:
    # Fallback if services.py is not available
    ScheduleService = None
    WaitlistService = None
    MakeupLessonService = None
    FinancialService = None
    NotificationService = None
    PredictiveService = None
    EnrollmentService = None
    PaymentGatewayService = None
    MercadoPagoService = None
    PagSeguroService = None
    StripeService = None
    PaymentGatewayManager = None
    payment_gateway_manager = None

__all__ = [
    'AnalyticsService',
    'RecitalService',
    'RecitalPDFGenerator',
    'ScheduleService',
    'WaitlistService',
    'MakeupLessonService',
    'FinancialService',
    'NotificationService',
    'PredictiveService',
    'EnrollmentService',
    'PaymentGatewayService',
    'MercadoPagoService',
    'PagSeguroService',
    'StripeService',
    'PaymentGatewayManager',
    'payment_gateway_manager'
]