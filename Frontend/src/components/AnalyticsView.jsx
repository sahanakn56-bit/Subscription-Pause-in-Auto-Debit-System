import React from 'react'

export default function AnalyticsView({ metrics }) {
  if (!metrics) return null

  return (
    <div className="analytics-view">
      <div className="analytics-header">
        <div>
          <h2>Executive Business & Churn Analytics</h2>
          <p className="analytics-subtitle">
            Evaluating the business efficacy and involuntary churn mitigation of the pause-aware layer (BRD Objectives BO-1 to BO-6).
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={() => alert('Audit logs exported successfully for compliance review (FR-34).')}
        >
          Export Compliance Audit (CSV)
        </button>
      </div>

      <div className="analytics-cards-grid">
        <div className="analytics-card">
          <span className="card-kpi-label">Pause-to-Resume Conversion Rate (BO-1)</span>
          <div className="card-kpi-value">{metrics.conversion_rate_percentage}%</div>
          <p className="card-kpi-desc">
            Percentage of customers who paused their recurring payment and subsequently resumed rather than completely cancelling their subscription.
          </p>
        </div>

        <div className="analytics-card">
          <span className="card-kpi-label">First-Debit Post-Resume Success Rate (BO-2)</span>
          <div className="card-kpi-value highlight-success">{metrics.resume_success_rate_percentage}%</div>
          <p className="card-kpi-desc">
            Success rate of first debits following resumption, enabled by pre-resume instrument and mandate verification.
          </p>
        </div>

        <div className="analytics-card">
          <span className="card-kpi-label">Involuntary vs. Voluntary Churn Separation (BO-3, FR-33)</span>
          <div className="churn-split-bar">
            <div className="churn-split-legend">
              <div>
                <span className="dot dot-involuntary"></span>
                <span>Involuntary Resumption Blocks ({metrics.involuntary_churn_count})</span>
              </div>
              <div>
                <span className="dot dot-voluntary"></span>
                <span>Voluntary Cancellations ({metrics.voluntary_churn_count})</span>
              </div>
            </div>
            <p className="card-kpi-desc">
              Failed debits due to card expiry or bank mandate lapse are separated from intentional churn, preventing skewed analytics.
            </p>
          </div>
        </div>
      </div>

      <div className="gap-analysis-table-card">
        <h3>Compliance & Rail Gap Mitigation Matrix</h3>
        <table className="gap-table">
          <thead>
            <tr>
              <th>Gap ID</th>
              <th>Payment Rail Limitation</th>
              <th>Orchestration Layer Solution</th>
              <th>Compliance Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>G1 / RULE-1</strong></td>
              <td>Mandate expires during pause</td>
              <td>Automatic safety margin computation caps pause length</td>
              <td><span className="pill pill-success">Enforced</span></td>
            </tr>
            <tr>
              <td><strong>G2 / RULE-3</strong></td>
              <td>Pre-debit notice missed on resume</td>
              <td>Pre-debit notifications scheduled 24-48h before presentation</td>
              <td><span className="pill pill-success">RBI Compliant</span></td>
            </tr>
            <tr>
              <td><strong>G3 / RULE-6</strong></td>
              <td>First debit fails due to expired card</td>
              <td>Pre-resume instrument health check blocks presentation on invalid cards</td>
              <td><span className="pill pill-success">Active</span></td>
            </tr>
            <tr>
              <td><strong>G4 / FR-19</strong></td>
              <td>Customer pauses mandate in bank app</td>
              <td>Webhook handler syncs state and notifies merchant without failed debits</td>
              <td><span className="pill pill-success">Synchronized</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
