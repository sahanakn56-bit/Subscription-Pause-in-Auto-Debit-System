import React, { useState, useEffect } from 'react'

export default function PauseModal({ subscription, role, onClose, onPauseSuccess }) {
  const [eligibility, setEligibility] = useState(null)
  const [loadingElig, setLoadingElig] = useState(true)
  const [pauseType, setPauseType] = useState('BOTH')
  const [durationDays, setDurationDays] = useState(30)
  const [reason, setReason] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)

  useEffect(() => {
    async function fetchEligibility() {
      try {
        setLoadingElig(true)
        setErrorMessage(null)
        const res = await fetch(`/api/subscriptions/${subscription.id}/pause-eligibility`)
        if (!res.ok) throw new Error('Failed to evaluate pause eligibility')
        const data = await res.json()
        setEligibility(data)
        if (data.max_allowed_pause_days > 0) {
          setDurationDays(Math.min(30, data.max_allowed_pause_days))
        }
      } catch (err) {
        setErrorMessage(err.message)
      } finally {
        setLoadingElig(false)
      }
    }
    fetchEligibility()
  }, [subscription.id])

  const calculateResumeDate = () => {
    const d = new Date()
    d.setDate(d.getDate() + Number(durationDays))
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setErrorMessage(null)

    try {
      const payload = {
        type: pauseType,
        duration_days: Number(durationDays),
        requested_by: role,
        reason: reason || 'Customer requested temporary hold',
        idempotency_key: `pause_${Date.now()}_${subscription.id}`,
      }

      const res = await fetch(`/api/subscriptions/${subscription.id}/pause`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to pause subscription')
      }

      onPauseSuccess(data)
    } catch (err) {
      setErrorMessage(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="pause-modal-title"
      >
        <div className="modal-header">
          <div>
            <h2 id="pause-modal-title" className="modal-title">Pause Subscription</h2>
            <p className="modal-subtitle">{subscription.plan_name} &bull; {subscription.currency} {subscription.amount}/mo</p>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close dialog">✕</button>
        </div>

        {errorMessage && (
          <div className="alert alert-danger" role="alert">
            <span aria-hidden="true">⚠️</span>
            <span>{errorMessage}</span>
          </div>
        )}

        {loadingElig ? (
          <div className="modal-loading" aria-live="polite">
            <div className="spinner" aria-hidden="true"></div>
            <p>Evaluating mandate validity and compliance safety margins...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="modal-form">
            {/* Eligibility Banner */}
            {eligibility && (
              <div className={`eligibility-box ${eligibility.is_eligible ? 'valid' : 'invalid'}`}>
                <div className="eligibility-status-row">
                  <span className="eligibility-icon" aria-hidden="true">
                    {eligibility.is_eligible ? '✅' : '🛑'}
                  </span>
                  <div>
                    <strong>
                      {eligibility.is_eligible ? 'Eligible for Auto-Debit Pause' : 'Pause Blocked by Payment Rail Rules'}
                    </strong>
                    <p className="eligibility-desc">
                      Mandate validity: {new Date(eligibility.mandate_valid_until).toLocaleDateString()} &bull; Safety margin: {eligibility.safety_margin_days} days.
                      {eligibility.is_eligible
                        ? ` Maximum safe pause duration: ${eligibility.max_allowed_pause_days} days.`
                        : ` ${(eligibility.rejection_reasons || []).join(', ')}`}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {eligibility?.is_eligible && (
              <>
                {/* Pause Type Selector (FR-7) */}
                <div className="form-group">
                  <label htmlFor="pause-type-select" className="form-label">
                    Pause Mode
                  </label>
                  <select
                    id="pause-type-select"
                    className="form-control"
                    value={pauseType}
                    onChange={(e) => setPauseType(e.target.value)}
                  >
                    <option value="BOTH">Both (Freeze Access & Stop All Billing)</option>
                    <option value="BILLING_ONLY">Billing Only (Maintain Access, Defer Next Charge)</option>
                    <option value="ACCESS_ONLY">Access Only (Temporarily Suspend Service Access)</option>
                  </select>
                  <p className="form-helper">
                    {pauseType === 'BOTH' && 'All auto-debit charges and service access will be paused.'}
                    {pauseType === 'BILLING_ONLY' && 'Customer keeps platform access while billing cycle is shifted.'}
                    {pauseType === 'ACCESS_ONLY' && 'Access is temporarily locked without modifying billing schedule.'}
                  </p>
                </div>

                {/* Duration Picker (FR-1, FR-3) */}
                <div className="form-group">
                  <label htmlFor="duration-slider" className="form-label">
                    Pause Duration: <strong>{durationDays} Days</strong>
                  </label>
                  <input
                    id="duration-slider"
                    type="range"
                    min="1"
                    max={eligibility.max_allowed_pause_days}
                    value={durationDays}
                    onChange={(e) => setDurationDays(e.target.value)}
                    className="slider-input"
                  />
                  <div className="preset-chips">
                    {[15, 30, 60, eligibility.max_allowed_pause_days]
                      .filter((val, idx, arr) => val <= eligibility.max_allowed_pause_days && arr.indexOf(val) === idx)
                      .map((days) => (
                        <button
                          key={days}
                          type="button"
                          className={`chip-btn ${durationDays == days ? 'active' : ''}`}
                          onClick={() => setDurationDays(days)}
                        >
                          {days === eligibility.max_allowed_pause_days ? `${days}d (Max)` : `${days} Days`}
                        </button>
                      ))}
                  </div>
                </div>

                {/* Transparent Impact Summary (No dark patterns) */}
                <div className="transparent-summary-card">
                  <span className="summary-title">Transparent Resumption Schedule</span>
                  <div className="summary-row">
                    <span>Auto-Debit Halts:</span>
                    <strong>Today (Immediately)</strong>
                  </div>
                  <div className="summary-row">
                    <span>Auto-Debit Resumes On:</span>
                    <strong>{calculateResumeDate()}</strong>
                  </div>
                  <div className="summary-row">
                    <span>Resumption Charge:</span>
                    <strong>{subscription.currency} {subscription.amount} (No hidden penalty)</strong>
                  </div>
                  <div className="summary-row">
                    <span>Pre-Debit Compliance Notice:</span>
                    <strong>Sent 48 hours prior via SMS/Email</strong>
                  </div>
                </div>

                {/* Reason Input */}
                <div className="form-group">
                  <label htmlFor="pause-reason" className="form-label">
                    Reason for Hold (Optional)
                  </label>
                  <input
                    id="pause-reason"
                    type="text"
                    className="form-control"
                    placeholder="e.g., Vacation, personal project break, budgeting"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </div>

                {/* Modal Actions */}
                <div className="modal-actions">
                  <button type="button" className="btn btn-secondary" onClick={onClose}>
                    Keep Subscription Active
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? 'Scheduling Pause...' : 'Confirm Subscription Pause'}
                  </button>
                </div>
              </>
            )}

            {!eligibility?.is_eligible && (
              <div className="modal-actions">
                <button type="button" className="btn btn-primary" onClick={onClose}>
                  Done
                </button>
              </div>
            )}
          </form>
        )}
      </div>
    </div>
  )
}
