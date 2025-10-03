"""
Configuration de django-auditlog : enregistrement des modèles à auditer
"""
from auditlog.registry import auditlog
from django.contrib.auth import get_user_model

# Import des modèles à auditer
from request.models import ProspectRequest
from offers.models import Offer
from billing.models import Product, Quote, QuoteLine, QuoteSignature
from installations.models import (
    Form, Signature, TechnicalVisit, RepresentationMandate,
    AdministrativeValidation, InstallationCompleted, ConsuelVisit,
    EnedisConnection, Commissioning
)
from invoices.models import Invoice, InvoiceLine, Installment, Payment
from administrative.models import (
    Cerfa16702, Cerfa16702Attachment, ElectricalDiagram, 
    EnedisMandate, Consuel
)
from planning.models import Task
from users.models import UserAccess, Role, Commission, PasswordResetToken
from admin_platform.models import EmailLog

User = get_user_model()

# ============================================
# Enregistrement des modèles
# ============================================

# Users
auditlog.register(
    User,
    exclude_fields=['password', 'last_login'],  # Ne pas logger les champs sensibles
    m2m_fields=['groups', 'user_permissions']   # Tracer les relations many-to-many
)
auditlog.register(UserAccess)
auditlog.register(Role)
auditlog.register(Commission)
# Pas besoin de logger PasswordResetToken (temporaire et sensible)

# Requests (Prospects/Demandes)
auditlog.register(ProspectRequest)

# Offers (Offres)
auditlog.register(Offer)

# Billing (Facturation)
auditlog.register(Product)
auditlog.register(Quote)
auditlog.register(QuoteLine)
auditlog.register(QuoteSignature)

# Installations
auditlog.register(Form)
auditlog.register(Signature)
auditlog.register(TechnicalVisit)
auditlog.register(RepresentationMandate)
auditlog.register(AdministrativeValidation)
auditlog.register(InstallationCompleted)
auditlog.register(ConsuelVisit)
auditlog.register(EnedisConnection)
auditlog.register(Commissioning)

# Invoices (Factures)
auditlog.register(Invoice)
auditlog.register(InvoiceLine)
auditlog.register(Installment)
auditlog.register(Payment)

# Administrative (Documents administratifs)
auditlog.register(Cerfa16702)
auditlog.register(Cerfa16702Attachment)
auditlog.register(ElectricalDiagram)
auditlog.register(EnedisMandate)
auditlog.register(Consuel)

# Planning
auditlog.register(Task)

# Admin Platform
auditlog.register(EmailLog)

