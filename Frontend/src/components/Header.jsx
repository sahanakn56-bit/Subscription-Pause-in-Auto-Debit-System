import React from 'react'

export default function Header({ role, setRole, activeTab, setActiveTab }) {
  return (
    <header className="app-header">
      <div className="header-container">
        <div className="brand">
          <div className="brand-logo" aria-hidden="true">⏸️</div>
          <div>
            <h1 className="brand-title">Auto-Debit Pause Layer</h1>
            <p className="brand-subtitle">Pause-Aware Orchestration for Recurring Payments</p>
          </div>
        </div>

        <div className="header-controls">
          <nav className="tab-nav" aria-label="Main Navigation">
            <button
              className={`tab-btn ${activeTab === 'subscriptions' ? 'active' : ''}`}
              onClick={() => setActiveTab('subscriptions')}
              aria-current={activeTab === 'subscriptions' ? 'page' : undefined}
            >
              Subscriptions
            </button>
            <button
              className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
              aria-current={activeTab === 'analytics' ? 'page' : undefined}
            >
              Analytics & Churn
            </button>
          </nav>

          <div className="role-selector">
            <label htmlFor="role-select" className="role-label">Actor Role:</label>
            <select
              id="role-select"
              className="role-select"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="CUSTOMER">Customer View</option>
              <option value="MERCHANT_ADMIN">Merchant Admin</option>
              <option value="SUPPORT_AGENT">Support Agent</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  )
}
