from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
import models


def reset_and_seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_data(force=True)


def seed_data(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded unless force=True
    if not force and db.query(models.Subscription).first():
        db.close()
        return

    now = datetime.utcnow()

    # 1. Mandates
    m1 = models.Mandate(
        id="man_upi_001",
        customer_id="cust_rahul",
        rail="UPI",
        status="ACTIVE",
        max_amount=5000.0,
        frequency="MONTHLY",
        valid_until=now + timedelta(days=120),  # 120 days valid
        rail_reference="upi-autopay-rahul-01"
    )
    m2 = models.Mandate(
        id="man_card_002",
        customer_id="cust_priya",
        rail="CARD",
        status="ACTIVE",
        max_amount=10000.0,
        frequency="MONTHLY",
        valid_until=now + timedelta(days=25),  # 25 days left (near expiry, test safety margin)
        rail_reference="tok_visa_priya_02"
    )
    m3 = models.Mandate(
        id="man_sepa_003",
        customer_id="cust_johan",
        rail="SEPA",
        status="ACTIVE",
        max_amount=150.0,
        frequency="MONTHLY",
        valid_until=now + timedelta(days=365),
        rail_reference="sepa-mandate-johan-03"
    )
    db.add_all([m1, m2, m3])
    db.flush()

    # 2. Payment Methods
    pm1 = models.PaymentMethod(
        id="pm_upi_001",
        customer_id="cust_rahul",
        type="UPI",
        details_masked="rahul@okaxis",
        health_status="HEALTHY",
        last_verified_at=now
    )
    pm2 = models.PaymentMethod(
        id="pm_card_002",
        customer_id="cust_priya",
        type="CARD",
        details_masked="Visa •••• 4242",
        expiry="12/28",
        health_status="HEALTHY",
        last_verified_at=now
    )
    pm3 = models.PaymentMethod(
        id="pm_card_expired",
        customer_id="cust_johan",
        type="CARD",
        details_masked="Mastercard •••• 8888",
        expiry="01/25",
        health_status="EXPIRED",
        last_verified_at=now - timedelta(days=30)
    )
    db.add_all([pm1, pm2, pm3])
    db.flush()

    # 3. Subscriptions
    sub1 = models.Subscription(
        id="sub_pro_rahul",
        merchant_id="merchant_cloud_saas",
        customer_id="cust_rahul",
        plan_id="plan_cloud_pro",
        plan_name="Cloud Pro Plan",
        amount=1499.0,
        currency="INR",
        status="ACTIVE",
        cycle_start=now - timedelta(days=15),
        cycle_end=now + timedelta(days=15),
        next_billing_at=now + timedelta(days=15),
        mandate_id=m1.id,
        payment_method_id=pm1.id
    )

    sub2 = models.Subscription(
        id="sub_ent_priya",
        merchant_id="merchant_cloud_saas",
        customer_id="cust_priya",
        plan_id="plan_enterprise",
        plan_name="Enterprise Suite",
        amount=4999.0,
        currency="INR",
        status="ACTIVE",
        cycle_start=now - timedelta(days=5),
        cycle_end=now + timedelta(days=25),
        next_billing_at=now + timedelta(days=25),
        mandate_id=m2.id,
        payment_method_id=pm2.id
    )

    sub3 = models.Subscription(
        id="sub_music_johan",
        merchant_id="merchant_cloud_saas",
        customer_id="cust_johan",
        plan_id="plan_music_family",
        plan_name="Music Family Plan",
        amount=19.99,
        currency="EUR",
        status="PAUSED",
        cycle_start=now - timedelta(days=40),
        cycle_end=now - timedelta(days=10),
        next_billing_at=now + timedelta(days=20),
        mandate_id=m3.id,
        payment_method_id=pm3.id
    )
    db.add_all([sub1, sub2, sub3])
    db.flush()

    # 4. Active Pause for sub3
    p1 = models.Pause(
        id="pause_sample_001",
        subscription_id=sub3.id,
        type="BOTH",
        start_at=now - timedelta(days=10),
        resume_at=now + timedelta(days=20),
        requested_by="CUSTOMER",
        reason="Vacation abroad",
        status="ACTIVE",
        policy_version=1
    )
    db.add(p1)

    # 5. Policies
    policy = models.PausePolicy(
        merchant_id="merchant_cloud_saas",
        version=1,
        allowed_types=["BILLING_ONLY", "ACCESS_ONLY", "BOTH"],
        max_length_days=90,
        cumulative_limit_days=180,
        date_policy="SHIFT",
        safety_margin_days=10,
        retry_policy={"max_retries": 3, "interval_days": 2}
    )
    db.add(policy)

    # 6. Audit event
    audit = models.AuditEvent(
        id="audit_init_001",
        subscription_id=sub3.id,
        event_type="subscription.paused",
        actor="CUSTOMER",
        timestamp=now - timedelta(days=10),
        payload={"pause_id": p1.id, "reason": "Vacation abroad"}
    )
    db.add(audit)

    db.commit()
    db.close()
    print("Database seeded successfully.")


if __name__ == "__main__":
    seed_data()
