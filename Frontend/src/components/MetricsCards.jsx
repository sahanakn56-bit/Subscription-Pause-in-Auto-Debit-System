import React from 'react'

export default function MetricsCards({ metrics, loading }) {
  if (loading || !metrics) {
    return (
      <div className="metrics-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="metric-card skeleton" aria-hidden="true">
            <div className="skeleton-title"></div>
            <div className="skeleton-val"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <span className="metric-label">Active Pauses</span>
        <div className="metric-value-wrap">
          <span className="metric-value">{metrics.active_pauses_count}</span>
          <span className="metric-pill info">Debits Withheld</span>
        </div>
        <p className="metric-subtext">Subscriptions currently under suppressed billing</p>
      </div>

      <div className="metric-card">
        <span className="metric-label">Upcoming Resumes (7 Days)</span>
        <div className="metric-value-wrap">
          <span className="metric-value">{metrics.upcoming_resumes_count}</span>
          <span className="metric-pill warning">Notices Scheduled</span>
        </div>
        <p className="metric-subtext">Pre-debit notifications and health checks pending</p>
      </div>

      <div className="metric-card">
        <span className="metric-label">Resume First-Debit Success</span>
        <div className="metric-value-wrap">
          <span className="metric-value">{metrics.resume_success_rate_percentage}%</span>
          <span className="metric-pill success">High Reliability</span>
        </div>
        <p className="metric-subtext">{metrics.resumed_total} successful debits after resumption</p>
      </div>

      <div className="metric-card">
        <span className="metric-label">Involuntary Churn Prevented</span>
        <div className="metric-value-wrap">
          <span className="metric-value">{metrics.involuntary_churn_count}</span>
          <span className="metric-pill danger">Failed Checks Caught</span>
        </div>
        <p className="metric-subtext">Expired instruments remediated before debit failure</p>
      </div>
    </div>
  )
}
