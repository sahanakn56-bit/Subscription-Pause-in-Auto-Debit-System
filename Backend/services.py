import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas


class PauseService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_default_policy(self, merchant_id: str) -> models.PausePolicy:
        policy = self.db.query(models.PausePolicy).filter(models.PausePolicy.merchant_id == merchant_id).first()
        if not policy:
            policy = models.PausePolicy(
                merchant_id=merchant_id,
                version=1,
                allowed_types=["BILLING_ONLY", "ACCESS_ONLY", "BOTH"],
                max_length_days=90,
                cumulative_limit_days=180,
                date_policy="SHIFT",
                safety_margin_days=10,
                retry_policy={"max_retries": 3, "interval_days": 2}
            )
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)
        return policy

    def check_eligibility(self, subscription_id: str) -> schemas.PauseEligibilityResponse:
        sub = self.db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
        if not sub:
            return schemas.PauseEligibilityResponse(
                subscription_id=subscription_id,
                is_eligible=False,
                rejection_reasons=["Subscription not found"],
                max_allowed_pause_days=0,
                mandate_valid_until=None,
                safety_margin_days=10,
                policy_max_days=90,
                allowed_types=[],
                suggested_resume_dates=[],
                requires_mandate_reauthorization=False,
            )

        policy = self.get_or_create_default_policy(sub.merchant_id)
        rejection_reasons = []
        is_eligible = True
        requires_reauth = False

        if sub.status != "ACTIVE":
            is_eligible = False
            rejection_reasons.append(f"Subscription is currently {sub.status}; only ACTIVE subscriptions can be paused.")

        mandate = sub.mandate
        mandate_valid_until = None
        max_from_mandate = policy.max_length_days

        if not mandate or mandate.status != "ACTIVE":
            is_eligible = False
            requires_reauth = True
            rejection_reasons.append("Underlying payment mandate is missing or not ACTIVE.")
        else:
            mandate_valid_until = mandate.valid_until
            days_until_expiry = (mandate.valid_until - datetime.utcnow()).days
            max_from_mandate = max(0, days_until_expiry - policy.safety_margin_days)
            if max_from_mandate <= 0:
                is_eligible = False
                requires_reauth = True
                rejection_reasons.append(
                    f"Mandate expires in {days_until_expiry} days, which violates the {policy.safety_margin_days}-day safety margin."
                )

        # Check cumulative pause limit in current cycle/period
        past_pauses = self.db.query(models.Pause).filter(
            models.Pause.subscription_id == subscription_id,
            models.Pause.status.in_(["ACTIVE", "COMPLETED"])
        ).all()
        used_pause_days = sum((p.resume_at - p.start_at).days for p in past_pauses if p.resume_at and p.start_at)
        remaining_cumulative = max(0, policy.cumulative_limit_days - used_pause_days)

        if remaining_cumulative <= 0:
            is_eligible = False
            rejection_reasons.append(f"Cumulative pause limit ({policy.cumulative_limit_days} days) exceeded.")

        effective_max = min(policy.max_length_days, max_from_mandate, remaining_cumulative)
        if effective_max <= 0:
            is_eligible = False

        suggested_dates = []
        now = datetime.utcnow()
        if is_eligible:
            for days in [15, 30, min(60, effective_max), effective_max]:
                if days > 0 and days <= effective_max:
                    suggested_dates.append(now + timedelta(days=days))

        return schemas.PauseEligibilityResponse(
            subscription_id=subscription_id,
            is_eligible=is_eligible,
            rejection_reasons=rejection_reasons,
            max_allowed_pause_days=max(0, effective_max),
            mandate_valid_until=mandate_valid_until,
            safety_margin_days=policy.safety_margin_days,
            policy_max_days=policy.max_length_days,
            allowed_types=policy.allowed_types,
            suggested_resume_dates=list(set(suggested_dates)),
            requires_mandate_reauthorization=requires_reauth,
        )

    def create_pause(self, subscription_id: str, req: schemas.PauseCreateRequest) -> schemas.PauseResponse:
        sub = self.db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
        if not sub:
            raise ValueError(f"Subscription {subscription_id} not found.")

        # Idempotency Check (FR-30)
        if req.idempotency_key:
            existing_audit = self.db.query(models.AuditEvent).filter(
                models.AuditEvent.subscription_id == subscription_id,
                models.AuditEvent.event_type == "subscription.pause_requested",
                models.AuditEvent.payload["idempotency_key"].as_string() == req.idempotency_key
            ).first()
            if existing_audit:
                active_pause = self.db.query(models.Pause).filter(
                    models.Pause.subscription_id == subscription_id,
                    models.Pause.status == "ACTIVE"
                ).first()
                if active_pause:
                    return schemas.PauseResponse.model_validate(active_pause)

        eligibility = self.check_eligibility(subscription_id)
        if not eligibility.is_eligible:
            raise ValueError(f"Pause request rejected: {'; '.join(eligibility.rejection_reasons)}")

        now = datetime.utcnow()
        start_at = req.start_at if req.start_at else now

        if req.resume_at:
            resume_at = req.resume_at
            requested_days = (resume_at - start_at).days
        elif req.duration_days:
            requested_days = req.duration_days
            resume_at = start_at + timedelta(days=requested_days)
        else:
            requested_days = 30
            resume_at = start_at + timedelta(days=30)

        if requested_days > eligibility.max_allowed_pause_days:
            raise ValueError(
                f"Requested pause of {requested_days} days exceeds maximum allowed limit of {eligibility.max_allowed_pause_days} days "
                f"(mandate expires with safety margin)."
            )

        policy = self.get_or_create_default_policy(sub.merchant_id)

        # Transition State Machine: ACTIVE -> PAUSED
        sub.status = "PAUSED"

        # Apply billing date policy (FR-8)
        if policy.date_policy == "SHIFT":
            sub.next_billing_at = resume_at
            sub.cycle_end = sub.cycle_end + timedelta(days=requested_days)
        elif policy.date_policy == "SKIP":
            sub.next_billing_at = resume_at

        pause_id = f"pause_{uuid.uuid4().hex[:8]}"
        new_pause = models.Pause(
            id=pause_id,
            subscription_id=sub.id,
            type=req.type,
            start_at=start_at,
            resume_at=resume_at,
            requested_by=req.requested_by,
            reason=req.reason,
            status="ACTIVE",
            policy_version=policy.version,
        )
        self.db.add(new_pause)

        # Create scheduled notifications (FR-21)
        # 1. Immediate Pause Confirmation
        notif_confirm = models.Notification(
            id=f"notif_{uuid.uuid4().hex[:8]}",
            subscription_id=sub.id,
            type="PAUSE_CONFIRMATION",
            channel="EMAIL",
            scheduled_at=now,
            sent_at=now,
            status="SENT",
            content=f"Your subscription {sub.plan_name} has been paused until {resume_at.strftime('%Y-%m-%d')}. No debits will occur during this period."
        )
        self.db.add(notif_confirm)

        # 2. Pre-Debit Notice scheduled 48h before resume (RBI / Compliance requirement)
        pre_notice_date = max(now, resume_at - timedelta(hours=48))
        notif_pre_debit = models.Notification(
            id=f"notif_{uuid.uuid4().hex[:8]}",
            subscription_id=sub.id,
            type="PRE_DEBIT_NOTICE",
            channel="SMS",
            scheduled_at=pre_notice_date,
            status="SCHEDULED",
            content=f"Notice: Auto-debit of {sub.currency} {sub.amount} for your {sub.plan_name} will resume on {resume_at.strftime('%Y-%m-%d')}."
        )
        self.db.add(notif_pre_debit)

        # Audit Event (FR-31)
        audit = models.AuditEvent(
            id=f"audit_{uuid.uuid4().hex[:8]}",
            subscription_id=sub.id,
            event_type="subscription.paused",
            actor=req.requested_by,
            payload={
                "pause_id": pause_id,
                "duration_days": requested_days,
                "start_at": start_at.isoformat(),
                "resume_at": resume_at.isoformat(),
                "idempotency_key": req.idempotency_key,
                "policy_version": policy.version,
            }
        )
        self.db.add(audit)

        self.db.commit()
        self.db.refresh(new_pause)
        return schemas.PauseResponse.model_validate(new_pause)

    def resume_subscription(self, subscription_id: str, req: schemas.ResumeRequest) -> schemas.ResumeResponse:
        sub = self.db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
        if not sub:
            raise ValueError(f"Subscription {subscription_id} not found.")

        if sub.status not in ["PAUSED", "PAUSE_REQUESTED", "RESUME_FAILED"]:
            raise ValueError(f"Subscription is in {sub.status} state; cannot resume.")

        now = datetime.utcnow()
        active_pause = self.db.query(models.Pause).filter(
            models.Pause.subscription_id == subscription_id,
            models.Pause.status == "ACTIVE"
        ).first()

        # Pre-Resume Verifications (FR-12)
        checks_summary = {
            "mandate_active": False,
            "mandate_not_expired": False,
            "payment_method_healthy": False,
            "advance_notification_lead_time_respected": True,
        }

        remediation_msg = None
        checks_passed = True

        # 1. Mandate health check
        mandate = sub.mandate
        if mandate and mandate.status == "ACTIVE":
            checks_summary["mandate_active"] = True
            if mandate.valid_until > now:
                checks_summary["mandate_not_expired"] = True
            else:
                checks_passed = False
                remediation_msg = "Underlying mandate has expired. Please re-authorize the mandate."
        else:
            checks_passed = False
            remediation_msg = f"Mandate is {mandate.status if mandate else 'MISSING'}. Mandate re-authorization required."

        # 2. Payment method health check (FR-12, FR-14)
        pm = sub.payment_method
        if pm and pm.health_status == "HEALTHY":
            checks_summary["payment_method_healthy"] = True
        else:
            checks_passed = False
            remediation_msg = "Payment instrument (card/account) has expired or is invalid. Please update payment method."

        if checks_passed:
            # Transition State: PAUSED -> ACTIVE (FR-13)
            sub.status = "ACTIVE"
            sub.next_billing_at = now if req.immediate else max(now, sub.next_billing_at)

            if active_pause:
                active_pause.status = "COMPLETED"

            # Create notification
            notif = models.Notification(
                id=f"notif_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                type="RESUME_CONFIRMATION",
                channel="EMAIL",
                scheduled_at=now,
                sent_at=now,
                status="SENT",
                content=f"Your subscription {sub.plan_name} has resumed. Next billing date is {sub.next_billing_at.strftime('%Y-%m-%d')}."
            )
            self.db.add(notif)

            # Record first debit attempt post-resume (FR-16)
            debit = models.DebitAttempt(
                id=f"deb_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                pause_id=active_pause.id if active_pause else None,
                amount=sub.amount,
                is_post_resume_first_debit=True,
                status="SUCCESS",
                attempt_number=1,
            )
            self.db.add(debit)

            # Audit Event
            audit = models.AuditEvent(
                id=f"audit_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                event_type="subscription.resumed",
                actor=req.requested_by,
                payload={"resumed_at": now.isoformat(), "immediate": req.immediate}
            )
            self.db.add(audit)
        else:
            # Transition State: RESUME_FAILED (FR-14)
            sub.status = "RESUME_FAILED"
            if active_pause:
                active_pause.status = "FAILED"

            # Tag failed debit attempt to track involuntary churn (FR-16, FR-33)
            debit = models.DebitAttempt(
                id=f"deb_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                pause_id=active_pause.id if active_pause else None,
                amount=sub.amount,
                is_post_resume_first_debit=True,
                status="FAILED",
                failure_reason=remediation_msg,
                is_involuntary_churn=True,
                attempt_number=1,
            )
            self.db.add(debit)

            # Remediation Notification
            notif = models.Notification(
                id=f"notif_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                type="RESUME_FAILURE",
                channel="EMAIL",
                scheduled_at=now,
                sent_at=now,
                status="SENT",
                content=f"Alert: Auto-debit resumption failed for {sub.plan_name}: {remediation_msg}"
            )
            self.db.add(notif)

            # Audit Event
            audit = models.AuditEvent(
                id=f"audit_{uuid.uuid4().hex[:8]}",
                subscription_id=sub.id,
                event_type="subscription.resume_failed",
                actor=req.requested_by,
                payload={"reason": remediation_msg, "checks_summary": checks_summary}
            )
            self.db.add(audit)

        self.db.commit()
        return schemas.ResumeResponse(
            subscription_id=sub.id,
            status=sub.status,
            resumed_at=now,
            next_billing_at=sub.next_billing_at,
            checks_passed=checks_passed,
            checks_summary=checks_summary,
            notification_sent=True,
            remediation_required=remediation_msg,
        )

    def handle_rail_webhook(self, payload: schemas.RailWebhookPayload) -> Dict[str, Any]:
        """Handles external customer-side rail events (e.g. customer paused mandate in UPI/bank app) (FR-18, FR-19)."""
        mandate = self.db.query(models.Mandate).filter(models.Mandate.rail_reference == payload.rail_reference).first()
        if not mandate:
            return {"status": "ignored", "reason": f"Mandate with ref {payload.rail_reference} not found"}

        now = datetime.utcnow()
        if payload.event_type == "mandate.paused":
            mandate.status = "PAUSED_BY_CUSTOMER"
            for sub in mandate.subscriptions:
                if sub.status == "ACTIVE":
                    sub.status = "PAUSED"
                audit = models.AuditEvent(
                    id=f"audit_{uuid.uuid4().hex[:8]}",
                    subscription_id=sub.id,
                    event_type="mandate.changed_by_customer",
                    actor="CUSTOMER_VIA_RAIL",
                    payload={"rail": payload.rail, "action": "customer_paused_mandate"}
                )
                self.db.add(audit)
        elif payload.event_type in ["mandate.revoked", "mandate.expired"]:
            mandate.status = "REVOKED" if "revoked" in payload.event_type else "EXPIRED"
            for sub in mandate.subscriptions:
                sub.status = "RESUME_FAILED" if sub.status == "PAUSED" else sub.status
                audit = models.AuditEvent(
                    id=f"audit_{uuid.uuid4().hex[:8]}",
                    subscription_id=sub.id,
                    event_type="mandate.changed_by_customer",
                    actor="CUSTOMER_VIA_RAIL",
                    payload={"rail": payload.rail, "action": "mandate_revoked_or_expired"}
                )
                self.db.add(audit)

        self.db.commit()
        return {"status": "processed", "mandate_id": mandate.id, "new_status": mandate.status}

    def get_analytics(self) -> schemas.AnalyticsResponse:
        """Returns business & compliance metrics distinguishing involuntary vs voluntary churn (FR-32, FR-33)."""
        active_pauses = self.db.query(models.Pause).filter(models.Pause.status == "ACTIVE").count()
        upcoming_resumes = self.db.query(models.Pause).filter(
            models.Pause.status == "ACTIVE",
            models.Pause.resume_at <= datetime.utcnow() + timedelta(days=7)
        ).count()

        resumed_total = self.db.query(models.DebitAttempt).filter(
            models.DebitAttempt.is_post_resume_first_debit == True,
            models.DebitAttempt.status == "SUCCESS"
        ).count()

        resume_failed_total = self.db.query(models.DebitAttempt).filter(
            models.DebitAttempt.is_post_resume_first_debit == True,
            models.DebitAttempt.status == "FAILED"
        ).count()

        total_first_debits = resumed_total + resume_failed_total
        success_rate = (resumed_total / total_first_debits * 100.0) if total_first_debits > 0 else 100.0

        involuntary_churn = self.db.query(models.DebitAttempt).filter(
            models.DebitAttempt.is_involuntary_churn == True
        ).count()

        voluntary_churn = self.db.query(models.Subscription).filter(
            models.Subscription.status == "CANCELLED"
        ).count()

        # Conversion rate: share of pauses that successfully resumed instead of cancelled (BO-1)
        total_resolved_pauses = resumed_total + voluntary_churn
        conversion_rate = (resumed_total / total_resolved_pauses * 100.0) if total_resolved_pauses > 0 else 85.0

        return schemas.AnalyticsResponse(
            active_pauses_count=active_pauses,
            upcoming_resumes_count=upcoming_resumes,
            resumed_total=resumed_total,
            resume_failed_total=resume_failed_total,
            resume_success_rate_percentage=round(success_rate, 1),
            involuntary_churn_count=involuntary_churn,
            voluntary_churn_count=voluntary_churn,
            conversion_rate_percentage=round(conversion_rate, 1),
        )
