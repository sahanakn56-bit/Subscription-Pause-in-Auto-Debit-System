import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
from database import Base, engine, SessionLocal
from seed import seed_data, reset_and_seed_data
import models

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    reset_and_seed_data()
    yield


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_subscriptions():
    response = client.get("/subscriptions")
    assert response.status_code == 200
    subs = response.json()
    assert isinstance(subs, list)
    assert len(subs) >= 1


def test_pause_eligibility_healthy_mandate():
    response = client.get("/subscriptions/sub_pro_rahul/pause-eligibility")
    assert response.status_code == 200
    data = response.json()
    assert data["subscription_id"] == "sub_pro_rahul"
    assert data["is_eligible"] is True
    assert data["max_allowed_pause_days"] > 0
    assert data["safety_margin_days"] == 10


def test_pause_eligibility_near_expiry_mandate():
    response = client.get("/subscriptions/sub_ent_priya/pause-eligibility")
    assert response.status_code == 200
    data = response.json()
    assert data["max_allowed_pause_days"] <= 20


def test_create_pause_success():
    payload = {
        "type": "BOTH",
        "duration_days": 14,
        "requested_by": "CUSTOMER",
        "reason": "Temporary break"
    }
    response = client.post("/subscriptions/sub_pro_rahul/pause", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["subscription_id"] == "sub_pro_rahul"

    # Verify subscription state updated to PAUSED
    sub_res = client.get("/subscriptions/sub_pro_rahul")
    assert sub_res.json()["status"] == "PAUSED"


def test_create_pause_exceeding_safety_margin_rejected():
    payload = {
        "type": "BOTH",
        "duration_days": 80,
        "requested_by": "CUSTOMER",
        "reason": "Exceeding validity"
    }
    response = client.post("/subscriptions/sub_ent_priya/pause", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed limit" in response.json()["detail"]


def test_resume_subscription_with_healthy_payment():
    # Pause first so it can be resumed
    client.post("/subscriptions/sub_pro_rahul/pause", json={"duration_days": 10})
    payload = {
        "requested_by": "CUSTOMER",
        "immediate": True
    }
    response = client.post("/subscriptions/sub_pro_rahul/resume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["checks_passed"] is True
    assert data["status"] == "ACTIVE"


def test_resume_subscription_fails_with_expired_instrument():
    # sub_music_johan has pm_card_expired -> Pre-resume check must fail
    payload = {
        "requested_by": "CUSTOMER",
        "immediate": True
    }
    response = client.post("/subscriptions/sub_music_johan/resume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["checks_passed"] is False
    assert data["status"] == "RESUME_FAILED"
    assert "expired or is invalid" in data["remediation_required"]


def test_rail_webhook_customer_side_pause():
    webhook_payload = {
        "rail": "UPI",
        "rail_reference": "upi-autopay-rahul-01",
        "event_type": "mandate.paused",
        "reason": "Customer paused in UPI app"
    }
    response = client.post("/webhooks/rail/UPI", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["new_status"] == "PAUSED_BY_CUSTOMER"


def test_get_metrics_analytics():
    response = client.get("/metrics/pause-analytics")
    assert response.status_code == 200
    data = response.json()
    assert "resume_success_rate_percentage" in data
    assert "involuntary_churn_count" in data
    assert "active_pauses_count" in data
