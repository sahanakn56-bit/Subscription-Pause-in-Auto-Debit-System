import React, { useState, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import MetricsCards from './components/MetricsCards'
import SubscriptionCard from './components/SubscriptionCard'
import PauseModal from './components/PauseModal'
import ResumeModal from './components/ResumeModal'
import AuditTrailDrawer from './components/AuditTrailDrawer'
import AnalyticsView from './components/AnalyticsView'

export default function App() {
  const [role, setRole] = useState('CUSTOMER')
  const [activeTab, setActiveTab] = useState('subscriptions')
  const [subscriptions, setSubscriptions] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toastMessage, setToastMessage] = useState(null)

  // Active modal targets
  const [selectedSubForPause, setSelectedSubForPause] = useState(null)
  const [selectedSubForResume, setSelectedSubForResume] = useState(null)
  const [selectedSubForAudit, setSelectedSubForAudit] = useState(null)

  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 5000)
  }

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [subsRes, metricsRes] = await Promise.all([
        fetch('/api/subscriptions'),
        fetch('/api/metrics/pause-analytics'),
      ])

      if (!subsRes.ok) throw new Error('Failed to fetch subscriptions')
      if (!metricsRes.ok) throw new Error('Failed to fetch pause metrics')

      const subsData = await subsRes.json()
      const metricsData = await metricsRes.json()

      setSubscriptions(subsData)
      setMetrics(metricsData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handlePauseSuccess = (pauseData) => {
    setSelectedSubForPause(null)
    showToast(`Subscription paused until ${new Date(pauseData.resume_at).toLocaleDateString()}. Debits are suppressed.`)
    loadData()
  }

  const handleResumeSuccess = (resumeData) => {
    setSelectedSubForResume(null)
    if (resumeData.checks_passed) {
      showToast(`Subscription resumed successfully! Pre-resume checks passed.`)
    } else {
      showToast(`Resumption blocked: ${resumeData.remediation_required}`)
    }
    loadData()
  }

  const handleSimulateRailEvent = async (sub) => {
    try {
      const res = await fetch(`/api/webhooks/rail/${sub.mandate.rail}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rail: sub.mandate.rail,
          rail_reference: sub.mandate.rail_reference,
          event_type: 'mandate.paused',
          reason: 'Customer toggled pause switch in UPI mobile app',
        }),
      })

      if (res.ok) {
        showToast(`Simulated customer UPI app pause! Mandate synced as PAUSED_BY_CUSTOMER.`)
        loadData()
      }
    } catch (e) {
      showToast('Failed to trigger simulated webhook event')
    }
  }

  return (
    <div className="app-layout">
      <Header
        role={role}
        setRole={setRole}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {toastMessage && (
        <div className="toast-notification" role="status" aria-live="polite">
          <span>🔔</span>
          <span>{toastMessage}</span>
          <button className="toast-close" onClick={() => setToastMessage(null)} aria-label="Close notification">✕</button>
        </div>
      )}

      <main className="main-content">
        <section className="metrics-section" aria-label="Operational Metrics">
          <MetricsCards metrics={metrics} loading={loading} />
        </section>

        {activeTab === 'subscriptions' ? (
          <section className="subscriptions-section">
            <div className="section-header">
              <div>
                <h2>Your Subscriptions & Recurring Mandates</h2>
                <p className="section-subtitle">
                  Manage active plans, schedule compliant auto-debit holds, and inspect mandate validity.
                </p>
              </div>
              <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
                {loading ? 'Refreshing...' : '🔄 Refresh Status'}
              </button>
            </div>

            {error && (
              <div className="alert alert-danger" role="alert">
                <strong>Error:</strong> {error}
              </div>
            )}

            {loading ? (
              <div className="cards-loading">
                <div className="spinner"></div>
                <p>Loading subscriptions and payment mandates from PostgreSQL...</p>
              </div>
            ) : subscriptions.length === 0 ? (
              <div className="empty-container">
                <p>No active subscriptions found.</p>
              </div>
            ) : (
              <div className="subscriptions-grid">
                {subscriptions.map((sub) => (
                  <SubscriptionCard
                    key={sub.id}
                    subscription={sub}
                    onOpenPause={(s) => setSelectedSubForPause(s)}
                    onOpenResume={(s) => setSelectedSubForResume(s)}
                    onViewAudit={(s) => setSelectedSubForAudit(s)}
                    onSimulateRailEvent={handleSimulateRailEvent}
                  />
                ))}
              </div>
            )}
          </section>
        ) : (
          <AnalyticsView metrics={metrics} />
        )}
      </main>

      {/* Modals & Drawers */}
      {selectedSubForPause && (
        <PauseModal
          subscription={selectedSubForPause}
          role={role}
          onClose={() => setSelectedSubForPause(null)}
          onPauseSuccess={handlePauseSuccess}
        />
      )}

      {selectedSubForResume && (
        <ResumeModal
          subscription={selectedSubForResume}
          role={role}
          onClose={() => setSelectedSubForResume(null)}
          onResumeSuccess={handleResumeSuccess}
        />
      )}

      {selectedSubForAudit && (
        <AuditTrailDrawer
          subscription={selectedSubForAudit}
          onClose={() => setSelectedSubForAudit(null)}
        />
      )}
    </div>
  )
}
