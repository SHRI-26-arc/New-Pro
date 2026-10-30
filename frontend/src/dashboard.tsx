
import { useState } from 'react'
import {
  LayoutDashboard,
  Truck,
  AlertTriangle,
  GitBranch,
  Activity,
  ClipboardCheck,
  Settings,
  LogOut,
  ChevronRight,
  Package,
} from 'lucide-react'

import './dashboard.css'

interface DashboardProps {
  onSignOut: () => void
}

const navigation = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Shipments', icon: Truck },
  { label: 'Disruptions', icon: AlertTriangle },
  { label: 'Recovery Planning', icon: GitBranch },
  { label: 'RippleGuard', icon: Activity },
  { label: 'Decision Passport', icon: ClipboardCheck },
]

const disruptionData = [
  {
    id: 'SH-2041',
    route: 'Pune → Bengaluru',
    issue: 'Severe weather',
    severity: 'High',
  },
  {
    id: 'SH-2118',
    route: 'Mumbai → Hyderabad',
    issue: 'Temperature alert',
    severity: 'Critical',
  },
  {
    id: 'SH-2193',
    route: 'Chennai → Kochi',
    issue: 'Transport congestion',
    severity: 'Medium',
  },
]

function Dashboard({ onSignOut }: DashboardProps) {
  const [activePage, setActivePage] = useState('Overview')

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">

        <div className="dashboard-brand">
          <div className="dashboard-logo">F</div>
          <span>FORESIGHT<span className="brand-x">X</span></span>
        </div>

        <p className="sidebar-label">WORKSPACE</p>

        <nav className="dashboard-navigation">
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              type="button"
              className={`nav-item ${
                activePage === label ? 'nav-active' : ''
              }`}
              onClick={() => setActivePage(label)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            className={`nav-item ${
              activePage === 'Settings' ? 'nav-active' : ''
            }`}
            onClick={() => setActivePage('Settings')}
          >
            <Settings size={18} />
            <span>Settings</span>
          </button>

          <div className="sidebar-user">
            <div className="user-avatar">OA</div>

            <div className="user-info">
              <strong>Operations Admin</strong>
              <span>Demo workspace</span>
            </div>

            <button
              className="signout-button"
              onClick={onSignOut}
              title="Sign out"
              aria-label="Sign out"
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>

      </aside>

      <main className="dashboard-main">

        <header className="dashboard-header">
          <div>
            <p className="dashboard-breadcrumb">
              WORKSPACE / {activePage.toUpperCase()}
            </p>

            <h1>
              {activePage === 'Overview'
                ? 'Overview'
                : activePage}
            </h1>

            <p className="header-description">
              Your supply chain at a glance.
            </p>
          </div>

          <span className="demo-label">DEMONSTRATION DATA</span>
        </header>

        {activePage === 'Overview' ? (

          <>

            <section className="metric-grid">

              <article className="simple-metric">
                <div className="metric-heading">
                  <Truck size={19} />
                  <span>Active shipments</span>
                </div>

                <strong>248</strong>

                <p>Shipments currently in transit</p>
              </article>

              <article className="simple-metric">
                <div className="metric-heading">
                  <AlertTriangle size={19} />
                  <span>Active disruptions</span>
                </div>

                <strong>06</strong>

                <p>Require operational attention</p>
              </article>

              <article className="simple-metric">
                <div className="metric-heading">
                  <Package size={19} />
                  <span>Inventory at risk</span>
                </div>

                <strong>12</strong>

                <p>Inventory locations requiring review</p>
              </article>

            </section>

            <section className="disruptions-section">

              <div className="section-header">
                <div>
                  <h2>Disruptions requiring attention</h2>
                  <p>Review the affected shipments and their current status.</p>
                </div>

                <button
                  className="text-button"
                  onClick={() => setActivePage('Disruptions')}
                >
                  View all <ChevronRight size={16} />
                </button>
              </div>

              <div className="disruption-list">

                {disruptionData.map((item) => (

                  <article className="disruption-row" key={item.id}>

                    <div className="disruption-info">
                      <strong>{item.id}</strong>
                      <span>{item.route}</span>
                    </div>

                    <div className="disruption-issue">
                      {item.issue}
                    </div>

                    <span
                      className={`severity-tag ${item.severity.toLowerCase()}`}
                    >
                      {item.severity}
                    </span>

                    <button
                      className="review-button"
                      onClick={() => setActivePage('Disruptions')}
                    >
                      Review <ChevronRight size={15} />
                    </button>

                  </article>

                ))}

              </div>

            </section>

            <section className="welcome-panel">
              <div>
                <span className="welcome-eyebrow">
                  FORESIGHTX INTELLIGENCE
                </span>

                <h2>See the risk before it unfolds.</h2>

                <p>
                  Explore recovery strategies and understand how one
                  supply-chain decision can affect the wider network.
                </p>
              </div>

              <button
                onClick={() => setActivePage('Recovery Planning')}
                className="explore-button"
              >
                Explore recovery planning
                <ChevronRight size={17} />
              </button>
            </section>

            <footer className="dashboard-footer">
              FORESIGHTX · Supply chain resilience platform
              <span>Prototype · Sample data</span>
            </footer>

          </>

        ) : (

          <section className="module-placeholder">
            <h2>{activePage}</h2>

            <p>
              This module will be developed in the next stage.
              Its navigation is available, but its functionality
              is not yet implemented.
            </p>

            <button
              onClick={() => setActivePage('Overview')}
              className="review-button"
            >
              Return to overview
            </button>
          </section>

        )}

      </main>
    </div>
  )
}

export default Dashboard
