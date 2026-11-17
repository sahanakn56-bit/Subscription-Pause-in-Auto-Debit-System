import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from './App'

const mockSubscriptions = [
  {
    id: 'sub_pro_rahul',
    merchant_id: 'merchant_cloud_saas',
    customer_id: 'cust_rahul',
    plan_id: 'plan_cloud_pro',
    plan_name: 'Cloud Pro Plan',
    amount: 1499.0,
    currency: 'INR',
    status: 'ACTIVE',
    cycle_start: '2026-11-01T00:00:00',
    cycle_end: '2026-12-01T00:00:00',
    next_billing_at: '2026-12-01T00:00:00',
    mandate: {
      id: 'man_upi_001',
      rail: 'UPI',
      status: 'ACTIVE',
      valid_until: '2027-03-01T00:00:00',
      max_amount: 5000.0,
      frequency: 'MONTHLY',
    },
    payment_method: {
      id: 'pm_upi_001',
      type: 'UPI',
      details_masked: 'rahul@okaxis',
      health_status: 'HEALTHY',
    },
  },
  {
    id: 'sub_music_johan',
    merchant_id: 'merchant_cloud_saas',
    customer_id: 'cust_johan',
    plan_id: 'plan_music_family',
    plan_name: 'Music Family Plan',
    amount: 19.99,
    currency: 'EUR',
    status: 'PAUSED',
    cycle_start: '2026-10-15T00:00:00',
    cycle_end: '2026-11-15T00:00:00',
    next_billing_at: '2026-12-15T00:00:00',
    mandate: {
      id: 'man_sepa_003',
      rail: 'SEPA',
      status: 'ACTIVE',
      valid_until: '2027-11-01T00:00:00',
      max_amount: 150.0,
      frequency: 'MONTHLY',
    },
    payment_method: {
      id: 'pm_card_expired',
      type: 'CARD',
      details_masked: 'Mastercard •••• 8888',
      health_status: 'EXPIRED',
    },
    active_pause: {
      id: 'pause_sample_001',
      subscription_id: 'sub_music_johan',
      type: 'BOTH',
      start_at: '2026-11-05T00:00:00',
      resume_at: '2026-12-05T00:00:00',
      reason: 'Vacation',
      status: 'ACTIVE',
      policy_version: 1,
    },
  },
]

const mockMetrics = {
  active_pauses_count: 1,
  upcoming_resumes_count: 1,
  resumed_total: 5,
  resume_failed_total: 1,
  resume_success_rate_percentage: 83.3,
  involuntary_churn_count: 1,
  voluntary_churn_count: 0,
  conversion_rate_percentage: 100.0,
}

describe('Frontend App Test Suite', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn((url) => {
        if (url.includes('pause-eligibility')) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                subscription_id: 'sub_pro_rahul',
                is_eligible: true,
                max_allowed_pause_days: 90,
                mandate_valid_until: '2027-03-01T00:00:00',
                safety_margin_days: 10,
                rejection_reasons: [],
                allowed_types: ['BOTH', 'BILLING_ONLY'],
              }),
          })
        }
        if (url.includes('/api/metrics/pause-analytics')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMetrics),
          })
        }
        if (url.includes('/api/subscriptions')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockSubscriptions),
          })
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
      })
    )
  })

  it('renders application header, metrics cards, and subscriptions', async () => {
    render(<App />)

    expect(screen.getByText('Auto-Debit Pause Layer')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Cloud Pro Plan')).toBeInTheDocument()
      expect(screen.getByText('Music Family Plan')).toBeInTheDocument()
    })

    // Check metric labels
    expect(screen.getByText('Active Pauses')).toBeInTheDocument()
    expect(screen.getByText('Upcoming Resumes (7 Days)')).toBeInTheDocument()
    expect(screen.getByText('Resume First-Debit Success')).toBeInTheDocument()
  })

  it('opens Pause Modal when Pause Subscription is clicked', async () => {
    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('Cloud Pro Plan')).toBeInTheDocument()
    })

    const pauseButton = screen.getByRole('button', { name: /Pause subscription for Cloud Pro Plan/i })
    fireEvent.click(pauseButton)

    await waitFor(() => {
      expect(screen.getByRole('dialog', { name: /Pause Subscription/i })).toBeInTheDocument()
      expect(screen.getByText(/Eligible for Auto-Debit Pause/i)).toBeInTheDocument()
      expect(screen.getByText('Transparent Resumption Schedule')).toBeInTheDocument()
    })
  })

  it('switches between Subscriptions and Analytics tabs', async () => {
    render(<App />)

    const analyticsTabBtn = screen.getByRole('button', { name: /Analytics & Churn/i })
    fireEvent.click(analyticsTabBtn)

    await waitFor(() => {
      expect(screen.getByText('Executive Business & Churn Analytics')).toBeInTheDocument()
      expect(screen.getByText('Compliance & Rail Gap Mitigation Matrix')).toBeInTheDocument()
    })
  })
})
