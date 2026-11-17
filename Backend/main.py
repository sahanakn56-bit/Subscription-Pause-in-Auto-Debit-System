from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas
from services import PauseService
from seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created and initial seed data is populated
    Base.metadata.create_all(bind=engine)
    try:
        seed_data()
    except Exception as e:
        print(f"Seed note: {e}")
    yield


app = FastAPI(
    title="Subscription Pause in Auto-Debit System API",
    description="Pause-Aware Orchestration Layer for Recurring Auto-Debit Payments (BRD/FRD v0.1 compliant)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "success",
        "service": "Subscription Pause Orchestration Layer",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# -------------------------------------------------------------
# Subscriptions Endpoints
# -------------------------------------------------------------
@app.get("/subscriptions", response_model=List[schemas.SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(models.Subscription).all()
    results = []
    for s in subs:
        active_p = db.query(models.Pause).filter(
            models.Pause.subscription_id == s.id,
            models.Pause.status == "ACTIVE"
        ).first()
        sub_resp = schemas.SubscriptionResponse.model_validate(s)
        if active_p:
            sub_resp.active_pause = schemas.PauseResponse.model_validate(active_p)
        results.append(sub_resp)
    return results


@app.get("/subscriptions/{id}", response_model=schemas.SubscriptionResponse)
def get_subscription(id: str, db: Session = Depends(get_db)):
    sub = db.query(models.Subscription).filter(models.Subscription.id == id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    active_p = db.query(models.Pause).filter(
        models.Pause.subscription_id == sub.id,
        models.Pause.status == "ACTIVE"
    ).first()
    resp = schemas.SubscriptionResponse.model_validate(sub)
    if active_p:
        resp.active_pause = schemas.PauseResponse.model_validate(active_p)
    return resp


# -------------------------------------------------------------
# Pause Eligibility Endpoint (FR-2 to FR-5)
# -------------------------------------------------------------
@app.get("/subscriptions/{id}/pause-eligibility", response_model=schemas.PauseEligibilityResponse)
def get_pause_eligibility(id: str, db: Session = Depends(get_db)):
    service = PauseService(db)
    return service.check_eligibility(id)


# -------------------------------------------------------------
# Pause Creation Endpoint (FR-1, FR-6 to FR-9)
# -------------------------------------------------------------
@app.post("/subscriptions/{id}/pause", response_model=schemas.PauseResponse)
def pause_subscription(id: str, req: schemas.PauseCreateRequest, db: Session = Depends(get_db)):
    service = PauseService(db)
    try:
        return service.create_pause(id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------------------------------------------
# Resume Endpoint (FR-12 to FR-15)
# -------------------------------------------------------------
@app.post("/subscriptions/{id}/resume", response_model=schemas.ResumeResponse)
def resume_subscription(id: str, req: schemas.ResumeRequest, db: Session = Depends(get_db)):
    service = PauseService(db)
    try:
        return service.resume_subscription(id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------------------------------------------
# Pause History & Audit Trail Endpoints (FR-31)
# -------------------------------------------------------------
@app.get("/subscriptions/{id}/pauses", response_model=List[schemas.PauseResponse])
def get_pause_history(id: str, db: Session = Depends(get_db)):
    pauses = db.query(models.Pause).filter(models.Pause.subscription_id == id).order_by(models.Pause.created_at.desc()).all()
    return pauses


@app.get("/subscriptions/{id}/audit-trail", response_model=List[schemas.AuditEventResponse])
def get_audit_trail(id: str, db: Session = Depends(get_db)):
    events = db.query(models.AuditEvent).filter(models.AuditEvent.subscription_id == id).order_by(models.AuditEvent.timestamp.desc()).all()
    return events


@app.get("/subscriptions/{id}/notifications", response_model=List[schemas.NotificationResponse])
def get_notifications(id: str, db: Session = Depends(get_db)):
    notifs = db.query(models.Notification).filter(models.Notification.subscription_id == id).order_by(models.Notification.scheduled_at.desc()).all()
    return notifs


# -------------------------------------------------------------
# Mandates & Policies Endpoints
# -------------------------------------------------------------
@app.get("/mandates/{id}", response_model=schemas.MandateResponse)
def get_mandate(id: str, db: Session = Depends(get_db)):
    mandate = db.query(models.Mandate).filter(models.Mandate.id == id).first()
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    return mandate


@app.put("/merchants/{id}/pause-policy", response_model=schemas.PausePolicyResponse)
def update_pause_policy(id: str, req: schemas.PausePolicyCreate, db: Session = Depends(get_db)):
    existing = db.query(models.PausePolicy).filter(models.PausePolicy.merchant_id == id).order_by(models.PausePolicy.version.desc()).first()
    new_version = (existing.version + 1) if existing else 1
    new_policy = models.PausePolicy(
        merchant_id=id,
        version=new_version,
        allowed_types=req.allowed_types,
        max_length_days=req.max_length_days,
        cumulative_limit_days=req.cumulative_limit_days,
        date_policy=req.date_policy,
        safety_margin_days=req.safety_margin_days,
        retry_policy=req.retry_policy,
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy


# -------------------------------------------------------------
# Rail Webhooks (FR-18, FR-19, FR-20)
# -------------------------------------------------------------
@app.post("/webhooks/rail/{rail}")
def handle_rail_webhook(rail: str, payload: schemas.RailWebhookPayload, db: Session = Depends(get_db)):
    service = PauseService(db)
    return service.handle_rail_webhook(payload)


# -------------------------------------------------------------
# Analytics & Metrics (FR-32, FR-33)
# -------------------------------------------------------------
@app.get("/metrics/pause-analytics", response_model=schemas.AnalyticsResponse)
def get_pause_analytics(db: Session = Depends(get_db)):
    service = PauseService(db)
    return service.get_analytics()
