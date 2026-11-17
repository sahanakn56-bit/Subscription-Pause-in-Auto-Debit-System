import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base


class Mandate(Base):
    __tablename__ = "mandates"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True, nullable=False)
    rail = Column(String, nullable=False)  # ACH, SEPA, UPI, CARD, NACH
    status = Column(String, default="ACTIVE", nullable=False)  # ACTIVE, PAUSED_BY_CUSTOMER, REVOKED, EXPIRED
    max_amount = Column(Float, nullable=False)
    frequency = Column(String, default="MONTHLY", nullable=False)
    valid_until = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, default=datetime.datetime.utcnow)
    rail_reference = Column(String, unique=True, nullable=True)  # e.g., UMRN, Token ID
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="mandate")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # UPI, CARD, BANK_ACCOUNT
    details_masked = Column(String, nullable=False)  # e.g. **** 4242 or user@okaxis
    expiry = Column(String, nullable=True)  # MM/YY for cards
    health_status = Column(String, default="HEALTHY", nullable=False)  # HEALTHY, EXPIRED, INVALID
    last_verified_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="payment_method")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    plan_id = Column(String, nullable=False)
    plan_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR", nullable=False)
    # States: ACTIVE, PAUSE_REQUESTED, PAUSED, RESUME_PENDING, RESUME_FAILED, CANCELLED
    status = Column(String, default="ACTIVE", nullable=False)
    cycle_start = Column(DateTime, nullable=False)
    cycle_end = Column(DateTime, nullable=False)
    next_billing_at = Column(DateTime, nullable=False)
    
    mandate_id = Column(String, ForeignKey("mandates.id"), nullable=True)
    payment_method_id = Column(String, ForeignKey("payment_methods.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    mandate = relationship("Mandate", back_populates="subscriptions")
    payment_method = relationship("PaymentMethod", back_populates="subscriptions")
    pauses = relationship("Pause", back_populates="subscription", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="subscription", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="subscription", cascade="all, delete-orphan")
    debit_attempts = relationship("DebitAttempt", back_populates="subscription", cascade="all, delete-orphan")


class PausePolicy(Base):
    __tablename__ = "pause_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(String, index=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    allowed_types = Column(JSON, default=["BILLING_ONLY", "ACCESS_ONLY", "BOTH"])
    max_length_days = Column(Integer, default=90)
    cumulative_limit_days = Column(Integer, default=180)
    date_policy = Column(String, default="SHIFT")  # SHIFT, SKIP, PRORATE
    safety_margin_days = Column(Integer, default=10)
    retry_policy = Column(JSON, default={"max_retries": 3, "interval_days": 2})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Pause(Base):
    __tablename__ = "pauses"

    id = Column(String, primary_key=True, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False, index=True)
    type = Column(String, default="BOTH", nullable=False)  # BILLING_ONLY, ACCESS_ONLY, BOTH
    start_at = Column(DateTime, nullable=False)
    resume_at = Column(DateTime, nullable=False)
    requested_by = Column(String, default="CUSTOMER", nullable=False)  # CUSTOMER, MERCHANT_ADMIN, SUPPORT_AGENT
    reason = Column(String, nullable=True)
    # Status: REQUESTED, ACTIVE, COMPLETED, CANCELLED, FAILED
    status = Column(String, default="ACTIVE", nullable=False)
    policy_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subscription = relationship("Subscription", back_populates="pauses")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # PAUSE_CONFIRMATION, UPCOMING_RESUME, PRE_DEBIT_NOTICE, RESUME_CONFIRMATION, RESUME_FAILURE, MANDATE_EXPIRING
    channel = Column(String, default="EMAIL", nullable=False)  # SMS, EMAIL, PUSH
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String, default="SCHEDULED", nullable=False)  # SCHEDULED, SENT, FAILED
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subscription = relationship("Subscription", back_populates="notifications")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # e.g., subscription.paused, subscription.resumed, mandate.changed_by_customer
    actor = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    payload = Column(JSON, nullable=True)

    subscription = relationship("Subscription", back_populates="audit_events")


class DebitAttempt(Base):
    __tablename__ = "debit_attempts"

    id = Column(String, primary_key=True, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False, index=True)
    pause_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    is_post_resume_first_debit = Column(Boolean, default=False)
    status = Column(String, default="PENDING")  # PENDING, SUCCESS, FAILED
    failure_reason = Column(String, nullable=True)
    is_involuntary_churn = Column(Boolean, default=False)
    attempt_number = Column(Integer, default=1)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    subscription = relationship("Subscription", back_populates="debit_attempts")
