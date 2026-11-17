import React, { useState, useEffect } from 'react'

export default function AuditTrailDrawer({ subscription, onClose }) {
  const [activeTab, setActiveTab] = useState('audit')
  const [auditEvents, setAuditEvents] = useState([])
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadLogs() {
      try {
        setLoading(true)
        const [auditRes, notifRes] = await Promise.all([
          fetch(`/api/subscriptions/${subscription.id}/audit-trail`),
          fetch(`/api/subscriptions/${subscription.id}/notifications`),
        ])
        if (auditRes.ok) setAuditEvents(await auditRes.json())
        if (notifRes.ok) setNotifications(await notifRes.json())
      } catch (e) {
        console.error('Failed to load audit events', e)
      } finally {
        setLoading(false)
      }
    }
    loadLogs()
  }, [subscription.id])

  const formatDate = (iso) => {
    if (!iso) return 'N/A'
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="drawer-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-drawer-title"
      >
        <div className="drawer-header">
          <div>
            <h2 id="audit-drawer-title" className="drawer-title">Audit Trail & Compliance Notices</h2>
            <p className="drawer-subtitle">{subscription.plan_name} (ID: {subscription.id})</p>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close drawer">✕</button>
        </div>

        <div className="drawer-tabs">
          <button
            className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Audit Events ({auditEvents.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            Compliance Notices ({notifications.length})
          </button>
        </div>

        <div className="drawer-content">
          {loading ? (
            <div className="modal-loading">
              <div className="spinner"></div>
              <p>Fetching immutable audit trail...</p>
            </div>
          ) : activeTab === 'audit' ? (
            <div className="timeline-list">
              {auditEvents.length === 0 ? (
                <p className="empty-state">No audit events recorded yet.</p>
              ) : (
                auditEvents.map((ev) => (
                  <div key={ev.id} className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-body">
                      <div className="timeline-header">
                        <span className="event-type-badge">{ev.event_type}</span>
                        <span className="timeline-date">{formatDate(ev.timestamp)}</span>
                      </div>
                      <p className="timeline-actor">Actor: <strong>{ev.actor}</strong></p>
                      {ev.payload && (
                        <pre className="timeline-payload">{JSON.stringify(ev.payload, null, 2)}</pre>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="notifications-list">
              {notifications.length === 0 ? (
                <p className="empty-state">No notifications recorded.</p>
              ) : (
                notifications.map((notif) => (
                  <div key={notif.id} className="notif-item">
                    <div className="notif-header">
                      <span className={`notif-status ${notif.status.toLowerCase()}`}>{notif.status}</span>
                      <span className="notif-channel">{notif.channel} &bull; {notif.type}</span>
                    </div>
                    <p className="notif-content">{notif.content}</p>
                    <span className="notif-time">Scheduled for: {formatDate(notif.scheduled_at)}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
