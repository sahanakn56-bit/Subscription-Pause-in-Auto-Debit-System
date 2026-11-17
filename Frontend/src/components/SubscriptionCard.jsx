import React from 'react'

export default function SubscriptionCard({
  subscription,
  onOpenPause,
  onOpenResume,
  onViewAudit,
  onSimulateRailEvent,
}) {
  const isPaused = subscription.status === 'PAUSED'
  const isActive = subscription.status === 'ACTIVE'
  const isFailed = subscription.status === 'RESUME_FAILED'

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ACTIVE':
        return <span className="status-badge status-active">Active</span>
      case 'PAUSED':
        return <span className="status-badge status-paused">Paused</span>
      case 'RESUME_PENDING':
        return <span className="status-badge status-pending">Resume Pending</span>
      case 'RESUME_FAILED':
        return <span className="status-badge status-failed">Resume Failed</span>
      case 'CANCELLED':
        return <span className="status-badge status-cancelled">Cancelled</span>
      default:
        return <span className="status-badge">{status}</span>
    }
  }

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A'
    return new Date(isoString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <article className="sub-card">
      <div className="sub-card-header">
        <div>
          <div className="sub-title-row">
            <h3 className="sub-plan-name">{subscription.plan_name}</h3>
            {getStatusBadge(subscription.status)}
          </div>
          <p className="sub-id">ID: <code>{subscription.id}</code> &bull; Customer: <strong>{subscription.customer_id}</strong></p>
        </div>
        <div className="sub-price">
          <span className="price-val">{subscription.currency} {subscription.amount.toLocaleString()}</span>
          <span className="price-freq">/ month</span>
        </div>
      </div>

      <div className="sub-details-grid">
        {/* Mandate Health Box */}
        <div className="info-box">
          <span className="info-label">Payment Mandate</span>
          <div className="info-row">
            <span className="rail-tag">{subscription.mandate?.rail || 'GENERIC'}</span>
            <span className={`health-indicator ${subscription.mandate?.status === 'ACTIVE' ? 'healthy' : 'warning'}`}>
              {subscription.mandate?.status || 'Active'}
            </span>
          </div>
          <p className="info-helper">
            Valid until: <strong>{formatDate(subscription.mandate?.valid_until)}</strong>
          </p>
        </div>

        {/* Payment Instrument Box */}
        <div className="info-box">
          <span className="info-label">Payment Instrument</span>
          <div className="info-row">
            <span className="instrument-name">{subscription.payment_method?.details_masked || 'Default Method'}</span>
            <span className={`health-indicator ${subscription.payment_method?.health_status === 'HEALTHY' ? 'healthy' : 'danger'}`}>
              {subscription.payment_method?.health_status || 'Healthy'}
            </span>
          </div>
          <p className="info-helper">
            Expires: <strong>{subscription.payment_method?.expiry || 'N/A'}</strong>
          </p>
        </div>

        {/* Billing Schedule Box */}
        <div className="info-box">
          <span className="info-label">Next Auto-Debit Date</span>
          <div className="info-row">
            <span className="next-billing-date">{formatDate(subscription.next_billing_at)}</span>
          </div>
          <p className="info-helper">
            Current cycle: {formatDate(subscription.cycle_start)} - {formatDate(subscription.cycle_end)}
          </p>
        </div>
      </div>

      {/* Active Pause Notice Banner */}
      {isPaused && subscription.active_pause && (
        <div className="pause-active-banner" role="alert">
          <div className="banner-icon" aria-hidden="true">⏸️</div>
          <div>
            <strong>Billing Paused ({subscription.active_pause.type.replace('_', ' ')})</strong>
            <p>
              Auto-debits suppressed from <strong>{formatDate(subscription.active_pause.start_at)}</strong> until{' '}
              <strong>{formatDate(subscription.active_pause.resume_at)}</strong>.
              Reason: <em>"{subscription.active_pause.reason || 'None specified'}"</em>
            </p>
          </div>
        </div>
      )}

      {isFailed && (
        <div className="pause-failed-banner" role="alert">
          <div className="banner-icon" aria-hidden="true">⚠️</div>
          <div>
            <strong>Auto-Debit Resumption Blocked</strong>
            <p>
              Pre-resume health checks failed. The payment instrument is expired or mandate needs re-consent. Please update payment method to resume service.
            </p>
          </div>
        </div>
      )}

      {/* Card Actions */}
      <div className="sub-card-actions">
        {isActive && (
          <button
            className="btn btn-primary"
            onClick={() => onOpenPause(subscription)}
            aria-label={`Pause subscription for ${subscription.plan_name}`}
          >
            Pause Subscription
          </button>
        )}

        {(isPaused || isFailed) && (
          <button
            className="btn btn-success"
            onClick={() => onOpenResume(subscription)}
            aria-label={`Resume subscription for ${subscription.plan_name}`}
          >
            Resume Auto-Debit
          </button>
        )}

        <button
          className="btn btn-secondary"
          onClick={() => onViewAudit(subscription)}
          aria-label={`View audit trail for ${subscription.plan_name}`}
        >
          Audit & Notices
        </button>

        {isActive && subscription.mandate?.rail === 'UPI' && (
          <button
            className="btn btn-ghost"
            title="Simulate customer pausing mandate in their UPI phone app (FR-18/19)"
            onClick={() => onSimulateRailEvent(subscription)}
          >
            Simulate App Pause
          </button>
        )}
      </div>
    </article>
  )
}
