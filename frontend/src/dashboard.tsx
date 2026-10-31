import { useState } from 'react'

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bell,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Database,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Package,
  Radio,
  ShieldAlert,
  Truck,
} from 'lucide-react'

import DisruptionDetails from './disruptiondetails'
import './dashboard.css'

interface DashboardProps {
  onSignOut: () => void
}

const navigation = [
  { label: 'Control Tower', icon: LayoutDashboard },
  { label: 'Disruption Details', icon: AlertTriangle },
  { label: 'Recovery Comparison', icon: GitBranch },
  { label: 'RippleGuard', icon: Activity },
  { label: 'Decision Passport', icon: ClipboardCheck },
] as const

type WorkflowPage = (typeof navigation)[number]['label']

const pageDescriptions: Record<WorkflowPage, string> = {
  'Control Tower':
    'Operational overview of the active pharmaceutical disruption scenario.',

  'Disruption Details':
    'Review the NH-44 closure, affected shipment TRK-104 and its operational constraints.',

  'Recovery Comparison':
    'Compare three recovery plans using arrival estimates, cost, inventory, downstream effects and compliance.',

  RippleGuard:
    'Inspect secondary risks, affected shipments, severity levels and the reasons behind each finding.',

  'Decision Passport':
    'Review supporting evidence, assumptions, warnings and the final human decision.',
}

const metrics = [
  {
    label: 'Active disruptions',
    value: '01',
    detail: 'NH-44 ROAD CLOSURE',
    icon: AlertTriangle,
    accent: 'amber',
  },
  {
    label: 'Affected shipments',
    value: '01',
    detail: 'TRK-104',
    icon: Truck,
    accent: 'cyan',
  },
  {
    label: 'Deliveries at risk',
    value: '01',
    detail: 'HOSPITAL A · BENGALURU',
    icon: Package,
    accent: 'red',
  },
  {
    label: 'Open evaluations',
    value: '00',
    detail: 'EVALUATION NOT YET RUN',
    icon: ClipboardCheck,
    accent: 'blue',
  },
]

const scenario = {
  shipment: 'TRK-104',
  disruption: 'NH-44 road closure',
  destination: 'Hospital A, Bengaluru',
  quantity: '200 medicine units',
  temperature: '2–8°C',
  deadline: '2:00 PM',
  eventTime: '10:15 AM',
  dataSource: 'Simulated scenario',
}

function StatusPill({
  value,
  tone,
}: {
  value: string
  tone: string
}) {
  return (
    <span className={`status-pill ${tone}`}>
      {value}
    </span>
  )
}

function Dashboard({ onSignOut }: DashboardProps) {
  const [activePage, setActivePage] =
    useState<WorkflowPage>('Control Tower')

  const selectedPage = navigation.find(
    (item) => item.label === activePage
  )

  const PageIcon = selectedPage?.icon ?? LayoutDashboard

  function openPage(page: WorkflowPage) {
    setActivePage(page)
  }

  return (
    <div className="dashboard-shell">

      {/* SIDEBAR */}

      <aside className="dashboard-sidebar">
        <div className="dashboard-brand">
          <div className="dashboard-logo">F</div>

          <div className="brand-wordmark">
            FORESIGHT<span>X</span>
            <small>INTELLIGENCE SYSTEMS</small>
          </div>
        </div>

        <div className="sidebar-section-label">
          WORKSPACE
        </div>

        <nav
          className="dashboard-navigation"
          aria-label="Main navigation"
        >
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              type="button"
              className={`nav-item ${
                activePage === label ? 'nav-active' : ''
              }`}
              aria-current={
                activePage === label ? 'page' : undefined
              }
              onClick={() => openPage(label)}
            >
              <Icon size={17} strokeWidth={1.8} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="operator-card">
            <div className="operator-avatar">OA</div>

            <div className="operator-info">
              <strong>OPERATIONS ADMIN</strong>
              <span>DEMO WORKSPACE</span>
            </div>

            <button
              type="button"
              className="signout-button"
              onClick={onSignOut}
              title="Sign out"
              aria-label="Sign out"
            >
              <LogOut size={16} />
            </button>
          </div>

          <div className="sidebar-version">
            FORESIGHTX SYSTEM · PROTOTYPE
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}

      <main className="dashboard-main">

        {/* GLOBAL HEADER */}

        <header className="command-header">
          <div className="header-title-group">
            <div className="command-breadcrumb">
              OPERATIONS CONSOLE
            </div>

            <h1>{activePage}</h1>

            <p>{pageDescriptions[activePage]}</p>
          </div>

          <div className="header-status-group">
            <div className="environment-label">
              <span className="environment-dot" />
              DEMONSTRATION ENVIRONMENT
            </div>

            <div className="system-indicator">
              <Radio size={14} />
              SIMULATED DATA
            </div>

            <button
              type="button"
              className="header-alert-button"
              onClick={() => openPage('Disruption Details')}
              aria-label="View active disruption"
              title="View active disruption"
            >
              <Bell size={17} />
              <span />
            </button>
          </div>
        </header>

        {/* PAGE 2 — DISRUPTION DETAILS */}

        {activePage === 'Disruption Details' ? (
          <DisruptionDetails
            {...scenario}
            onContinue={() => openPage('Recovery Comparison')}
          />

        ) : activePage === 'Control Tower' ? (
          <>
            {/* OPERATIONAL OVERVIEW */}

            <div className="overview-intro">
              <div>
                <span className="section-kicker">
                  OPERATIONAL STATUS
                </span>

                <h2>Network overview</h2>
              </div>

              <span className="sample-indicator">
                SIMULATED SCENARIO
              </span>
            </div>

            {/* KEY METRICS */}

            <section
              className="metric-grid"
              aria-label="Control Tower metrics"
            >
              {metrics.map((metric) => {
                const Icon = metric.icon

                return (
                  <article
                    className="metric-card"
                    key={metric.label}
                  >
                    <div className="metric-card-top">
                      <span>{metric.label}</span>

                      <Icon
                        className={`metric-icon ${metric.accent}`}
                        size={19}
                      />
                    </div>

                    <div className="metric-value">
                      {metric.value}
                    </div>

                    <div
                      className={`metric-detail ${metric.accent}`}
                    >
                      <span className="metric-status-dot" />
                      {metric.detail}
                    </div>
                  </article>
                )
              })}
            </section>

            {/* ACTIVE SHIPMENT AND DISRUPTION */}

            <section className="primary-grid">
              <article className="command-panel shipment-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">
                      AFFECTED SHIPMENT
                    </span>

                    <h3>{scenario.shipment}</h3>

                    <p>
                      Pharmaceutical delivery requiring
                      temperature-controlled transportation.
                    </p>
                  </div>

                  <Truck
                    size={19}
                    className="panel-accent-icon"
                  />
                </div>

                <div className="table-scroll">
                  <table className="shipment-table">
                    <thead>
                      <tr>
                        <th>SHIPMENT</th>
                        <th>DESTINATION</th>
                        <th>QUANTITY</th>
                        <th>DEADLINE</th>
                        <th>STATUS</th>
                      </tr>
                    </thead>

                    <tbody>
                      <tr>
                        <td>
                          <strong className="shipment-reference">
                            {scenario.shipment}
                          </strong>
                        </td>

                        <td>
                          <span className="shipment-route">
                            {scenario.destination}
                          </span>
                        </td>

                        <td>{scenario.quantity}</td>

                        <td className="shipment-eta">
                          {scenario.deadline}
                        </td>

                        <td>
                          <StatusPill
                            value="AT RISK"
                            tone="critical"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="mission-checklist">
                  <div>
                    <Package size={15} />
                    <span>Medicine quantity</span>
                    <strong>200 UNITS</strong>
                  </div>

                  <div>
                    <Clock3 size={15} />
                    <span>Delivery deadline</span>
                    <strong>2:00 PM</strong>
                  </div>

                  <div>
                    <ShieldAlert size={15} />
                    <span>Cold-chain requirement</span>
                    <strong>2–8°C</strong>
                  </div>
                </div>

                <button
                  type="button"
                  className="panel-action"
                  onClick={() => openPage('Disruption Details')}
                >
                  Review disruption details
                  <ArrowRight size={15} />
                </button>
              </article>

              <article className="command-panel mission-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">
                      ACTIVE DISRUPTION
                    </span>

                    <h3>NH-44 road closure</h3>

                    <p>
                      A simulated road closure affecting
                      pharmaceutical transportation.
                    </p>
                  </div>

                  <AlertTriangle
                    size={19}
                    className="panel-accent-icon"
                  />
                </div>

                <div className="mission-status-block">
                  <div className="mission-status-heading">
                    <span>INCIDENT STATUS</span>

                    <StatusPill
                      value="ACTIVE"
                      tone="critical"
                    />
                  </div>

                  <h4>Delivery at risk</h4>

                  <p>
                    The simulated closure affects the planned
                    journey of {scenario.shipment}.
                    The delivery deadline remains {scenario.deadline}.
                  </p>
                </div>

                <div className="mission-checklist">
                  <div>
                    <Clock3 size={15} />
                    <span>Reported at</span>
                    <strong>{scenario.eventTime}</strong>
                  </div>

                  <div>
                    <Truck size={15} />
                    <span>Affected shipment</span>
                    <strong>{scenario.shipment}</strong>
                  </div>

                  <div>
                    <Package size={15} />
                    <span>Destination</span>
                    <strong>HOSPITAL A</strong>
                  </div>
                </div>

                <button
                  type="button"
                  className="panel-action"
                  onClick={() => openPage('Disruption Details')}
                >
                  Open incident
                  <ArrowRight size={15} />
                </button>
              </article>
            </section>

            {/* EVALUATION AND SYSTEM STATUS */}

            <section className="secondary-grid">
              <article className="command-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">
                      RECOVERY WORKFLOW
                    </span>

                    <h3>Evaluation progress</h3>

                    <p>
                      Current stage of the demonstration scenario.
                    </p>
                  </div>

                  <Activity
                    size={18}
                    className="panel-accent-icon"
                  />
                </div>

                <div className="mission-checklist">
                  <div>
                    <CheckCircle2 size={15} />
                    <span>Scenario data loaded</span>
                    <strong>READY</strong>
                  </div>

                  <div>
                    <CheckCircle2 size={15} />
                    <span>Disruption identified</span>
                    <strong>READY</strong>
                  </div>

                  <div>
                    <Clock3 size={15} />
                    <span>Recovery evaluation</span>
                    <strong>NOT RUN</strong>
                  </div>

                  <div>
                    <Clock3 size={15} />
                    <span>Recovery plan comparison</span>
                    <strong>WAITING</strong>
                  </div>

                  <div>
                    <ShieldAlert size={15} />
                    <span>Human review</span>
                    <strong>PENDING</strong>
                  </div>
                </div>

                <button
                  type="button"
                  className="panel-action"
                  onClick={() => openPage('Disruption Details')}
                >
                  Continue to disruption details
                  <ArrowRight size={15} />
                </button>
              </article>

              <article className="command-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">
                      DATA & CONNECTIVITY
                    </span>

                    <h3>System status</h3>

                    <p>
                      Current source and integration status.
                    </p>
                  </div>

                  <Database
                    size={18}
                    className="panel-accent-icon"
                  />
                </div>

                <div className="mission-checklist">
                  <div>
                    <Radio size={15} />
                    <span>Scenario data</span>
                    <strong>SAMPLE DATA</strong>
                  </div>

                  <div>
                    <Database size={15} />
                    <span>SAP HANA Cloud</span>
                    <strong>NOT VERIFIED</strong>
                  </div>

                  <div>
                    <Activity size={15} />
                    <span>Live operational feed</span>
                    <strong>NOT CONNECTED</strong>
                  </div>
                </div>

                <p>
                  All displayed scenario information is illustrative.
                  No live shipment, supplier or SAP connection is
                  represented here.
                </p>
              </article>
            </section>

            <footer className="dashboard-footer">
              <span>FORESIGHTX INTELLIGENCE SYSTEMS</span>

              <span>
                PROTOTYPE · SIMULATED DATA · HUMAN APPROVAL REQUIRED
              </span>
            </footer>
          </>

        ) : (

          /* OTHER WORKFLOW PAGES — TEMPORARY PLACEHOLDERS */

          <section className="module-placeholder">
            <div className="placeholder-icon">
              <PageIcon size={25} />
            </div>

            <span className="panel-kicker">
              NEXT WORKFLOW STAGE
            </span>

            <h2>{activePage}</h2>

            <p>{pageDescriptions[activePage]}</p>

            <StatusPill
              value="NOT YET IMPLEMENTED"
              tone="under-review"
            />

            <button
              type="button"
              className="panel-action"
              onClick={() => openPage('Control Tower')}
            >
              Return to Control Tower
              <ArrowRight size={15} />
            </button>
          </section>
        )}
      </main>
    </div>
  )
}

export default Dashboard