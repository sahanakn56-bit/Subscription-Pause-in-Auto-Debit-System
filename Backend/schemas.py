from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# -------------------------------------------------------------
# Mandate & Payment Method Schemas
# -------------------------------------------------------------
class MandateBase(BaseModel):
    id: str
    customer_id: str
    rail: str  # ACH, SEPA, UPI, CARD, NACH
    status: str
    max_amount: float
    frequency: str
    valid_until: datetime
    rail_reference: Optional[str] = None


class MandateResponse(MandateBase):
    model_config = ConfigDict(from_attributes=True)
    last_used_at: Optional[datetime] = None
    created_at: datetime


class PaymentMethodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    customer_id: str
    type: str
    details_masked: str
    expiry: Optional[str] = None
    health_status: str
    last_verified_at: Optional[datetime] = None


# -------------------------------------------------------------
# Pause Policy Schemas
# -------------------------------------------------------------
class PausePolicyBase(BaseModel):
    merchant_id: str
    version: int = 1
    allowed_types: List[str] = ["BILLING_ONLY", "ACCESS_ONLY", "BOTH"]
    max_length_days: int = Field(default=90, ge=1)
    cumulative_limit_days: int = Field(default=180, ge=1)
    date_policy: str = "SHIFT"  # SHIFT, SKIP, PRORATE
    safety_margin_days: int = Field(default=10, ge=0)
    retry_policy: Dict[str, Any] = {"max_retries": 3, "interval_days": 2}


class PausePolicyCreate(PausePolicyBase):
    pass


class PausePolicyResponse(PausePolicyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# -------------------------------------------------------------
# Pause Eligibility Schemas (FR-2, FR-3, FR-4, FR-5)
# -------------------------------------------------------------
class PauseEligibilityResponse(BaseModel):
    subscription_id: str
    is_eligible: bool
    rejection_reasons: List[str] = []
    max_allowed_pause_days: int
    mandate_valid_until: Optional[datetime] = None
    safety_margin_days: int
    policy_max_days: int
    allowed_types: List[str] = []
    suggested_resume_dates: List[datetime] = []
    requires_mandate_reauthorization: bool = False


# -------------------------------------------------------------
# Pause Action Schemas (FR-1, FR-6, FR-7, FR-8, FR-9)
# -------------------------------------------------------------
class PauseCreateRequest(BaseModel):
    type: str = Field(default="BOTH", description="BILLING_ONLY, ACCESS_ONLY, or BOTH")
    duration_days: Optional[int] = Field(default=None, ge=1)
    resume_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    requested_by: str = Field(default="CUSTOMER", description="CUSTOMER, MERCHANT_ADMIN, or SUPPORT_AGENT")
    reason: Optional[str] = None
    idempotency_key: Optional[str] = None


class PauseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subscription_id: str
    type: str
    start_at: datetime
    resume_at: datetime
    requested_by: str
    reason: Optional[str] = None
    status: str
    policy_version: int
    created_at: datetime


# -------------------------------------------------------------
# Resume Schemas (FR-12, FR-13, FR-14, FR-15)
# -------------------------------------------------------------
class ResumeRequest(BaseModel):
    requested_by: str = Field(default="CUSTOMER", description="CUSTOMER, MERCHANT_ADMIN, or SYSTEM")
    immediate: bool = False
    idempotency_key: Optional[str] = None


class ResumeResponse(BaseModel):
    subscription_id: str
    status: str
    resumed_at: datetime
    next_billing_at: datetime
    checks_passed: bool
    checks_summary: Dict[str, Any]
    notification_sent: bool
    remediation_required: Optional[str] = None


# -------------------------------------------------------------
# Subscription Full Schemas
# -------------------------------------------------------------
class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    merchant_id: str
    customer_id: str
    plan_id: str
    plan_name: str
    amount: float
    currency: str
    status: str
    cycle_start: datetime
    cycle_end: datetime
    next_billing_at: datetime
    mandate_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    created_at: datetime
    mandate: Optional[MandateResponse] = None
    payment_method: Optional[PaymentMethodResponse] = None
    active_pause: Optional[PauseResponse] = None


# -------------------------------------------------------------
# Notification & Audit Schemas (FR-21, FR-31)
# -------------------------------------------------------------
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subscription_id: str
    type: str
    channel: str
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: str
    content: str
    created_at: datetime


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subscription_id: str
    event_type: str
    actor: str
    timestamp: datetime
    payload: Optional[Dict[str, Any]] = None


# -------------------------------------------------------------
# Webhook Schemas (FR-18, FR-19, FR-20)
# -------------------------------------------------------------
class RailWebhookPayload(BaseModel):
    rail: str
    rail_reference: str
    event_type: str  # mandate.paused, mandate.revoked, mandate.expired, debit.failed
    reason: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


# -------------------------------------------------------------
# Analytics & Metrics Schemas (FR-32, FR-33)
# -------------------------------------------------------------
class AnalyticsResponse(BaseModel):
    active_pauses_count: int
    upcoming_resumes_count: int
    resumed_total: int
    resume_failed_total: int
    resume_success_rate_percentage: float
    involuntary_churn_count: int
    voluntary_churn_count: int
    conversion_rate_percentage: float
