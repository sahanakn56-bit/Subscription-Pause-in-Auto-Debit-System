import React, { useState } from 'react'

export default function ResumeModal({ subscription, role, onClose, onResumeSuccess }) {
  const [immediate, setImmediate] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [result, setResult] = useState(null)

  const handleResume = async () => {
    setSubmitting(true)
    setErrorMessage(null)

    try {
      const payload = {
        requested_by: role,
        immediate: immediate,
        idempotency_key: `resume_${Date.now()}_${subscription.id}`,
      }

      const res = await fetch(`/api/subscriptions/${subscription.id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to resume subscription')
      }

      setResult(data)
      if (data.checks_passed) {
        setTimeout(() => {
          onResumeSuccess(data)
        }, 1500)
      }
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
        aria-labelledby="resume-modal-title"
      >
        <div className="modal-header">
          <div>
            <h2 id="resume-modal-title" className="modal-title">Resume Auto-Debit</h2>
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

        {result ? (
          <div className="resume-result-view">
            <div className={`result-header ${result.checks_passed ? 'success' : 'failure'}`}>
              <span className="result-icon">{result.checks_passed ? '🎉' : '⚠️'}</span>
              <h3>{result.checks_passed ? 'Pre-Resume Verification Passed' : 'Pre-Resume Check Failed'}</h3>
            </div>

            <div className="checks-list">
              <div className="check-item">
                <span>Payment Mandate Active & Valid:</span>
                <strong>{result.checks_summary.mandate_not_expired ? 'Passed ✅' : 'Failed ❌'}</strong>
              </div>
              <div className="check-item">
                <span>Payment Instrument Healthy:</span>
                <strong>{result.checks_summary.payment_method_healthy ? 'Passed ✅' : 'Failed ❌'}</strong>
              </div>
              <div className="check-item">
                <span>Pre-Debit Compliance Lead Time:</span>
                <strong>{result.checks_summary.advance_notification_lead_time_respected ? 'Verified ✅' : 'Warning ⚠️'}</strong>
              </div>
            </div>

            {result.remediation_required && (
              <div className="remediation-box" role="alert">
                <strong>Remediation Required:</strong>
                <p>{result.remediation_required}</p>
                <p className="remediation-note">
                  The auto-debit system stopped an involuntary failure from occurring. Please update your payment card/details.
                </p>
              </div>
            )}

            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  onResumeSuccess(result)
                  onClose()
                }}
              >
                Close & Refresh
              </button>
            </div>
          </div>
        ) : (
          <div className="resume-pre-flow">
            <p className="resume-explainer">
              Resuming will re-activate recurring auto-debit billing against your registered mandate.
              A pre-resume verification will run automatically before presenting any charge to ensure your card or bank account is valid and in good standing.
            </p>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={immediate}
                  onChange={(e) => setImmediate(e.target.checked)}
                />
                <span>Resume immediately and schedule the first post-pause debit cycle now</span>
              </label>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Keep Paused
              </button>
              <button
                type="button"
                className="btn btn-success"
                onClick={handleResume}
                disabled={submitting}
              >
                {submitting ? 'Running Pre-Resume Verification...' : 'Execute Pre-Resume & Unpause'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
