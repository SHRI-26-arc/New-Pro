import type { ReactNode } from 'react'

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  Database,
  Info,
  MapPin,
  Package,
  Route,
  ShieldCheck,
  Thermometer,
} from 'lucide-react'

import './disruptiondetails.css'

interface DisruptionDetailsProps {
  shipment: string
  disruption: string
  destination: string
  quantity: string
  temperature: string
  deadline: string
  eventTime: string
  dataSource: string
  onContinue: () => void
}

function Fact({
  label,
  value,
  icon,
}: {
  label: string
  value: string
  icon?: ReactNode
}) {
  return (
    <div className="incident-fact">
      <span className="incident-fact-label">{label}</span>
      <strong>
        {icon}
        {value}
      </strong>
    </div>
  )
}

function DisruptionDetails({
  shipment,
  disruption,
  destination,
  quantity,
  temperature,
  deadline,
  eventTime,
  dataSource,
  onContinue,
}: DisruptionDetailsProps) {
  return (
    <div className="incident-page">

      {/* INCIDENT BANNER */}

      <section className="incident-banner">
        <div className="incident-banner-main">
          <div className="incident-banner-icon">
            <AlertTriangle size={21} />
          </div>

          <div>
            <span className="incident-eyebrow">
              ACTIVE DISRUPTION · {dataSource.toUpperCase()}
            </span>

            <h2>{disruption}</h2>

            <p>
              A transportation disruption has put shipment {shipment}
              at risk. Its delivery requirements must be considered
              before selecting a recovery plan.
            </p>
          </div>
        </div>

        <div className="incident-banner-meta">
          <span className="incident-status">
            <span />
            ACTIVE
          </span>

          <span className="incident-reported">
            <Clock3 size={14} />
            Reported at {eventTime}
          </span>
        </div>
      </section>

      {/* FOUR INFORMATION SECTIONS */}

      <section
        className="incident-sections"
        aria-label="Disruption information"
      >

        {/* 01 — SHIPMENT PROFILE */}

        <article className="incident-section incident-shipment">
          <div className="incident-section-heading">
            <div>
              <span className="incident-section-number">
                01 / SHIPMENT PROFILE
              </span>

              <h3>Shipment overview</h3>

              <p>
                Identity and delivery details of the affected cargo.
              </p>
            </div>

            <Package size={20} />
          </div>

          <div className="incident-shipment-id">
            <span>SHIPMENT REFERENCE</span>
            <strong>{shipment}</strong>
          </div>

          <div className="incident-fact-grid">
            <Fact label="CARGO" value="IV medicine" />
            <Fact label="QUANTITY" value={quantity} />

            <Fact
              label="DESTINATION"
              value={destination}
              icon={<MapPin size={14} />}
            />

            <Fact
              label="DELIVERY DEADLINE"
              value={deadline}
              icon={<Clock3 size={14} />}
            />
          </div>

          <div className="incident-footnote">
            <Info size={15} />
            <span>
              Origin and more detailed cargo specifications
              are not available in the current scenario.
            </span>
          </div>
        </article>

        {/* 02 — INCIDENT INFORMATION */}

        <article className="incident-section incident-event">
          <div className="incident-section-heading">
            <div>
              <span className="incident-section-number">
                02 / INCIDENT INFORMATION
              </span>

              <h3>Disruption details</h3>

              <p>
                The event affecting the shipment's planned journey.
              </p>
            </div>

            <AlertTriangle size={20} />
          </div>

          <div className="incident-event-highlight">
            <span>REPORTED DISRUPTION</span>

            <strong>{disruption}</strong>

            <span className="incident-event-time">
              <Clock3 size={14} />
              {eventTime}
            </span>
          </div>

          <div className="incident-fact-grid">
            <Fact
              label="AFFECTED ROUTE"
              value="NH-44"
              icon={<Route size={14} />}
            />

            <Fact label="EVENT STATUS" value="Active" />
            <Fact label="AFFECTED SHIPMENT" value={shipment} />

            <Fact
              label="DATA SOURCE"
              value={dataSource}
              icon={<Database size={14} />}
            />
          </div>

          <div className="incident-footnote">
            <Info size={15} />
            <span>
              The exact road-closure location and affected
              road segment have not been supplied.
            </span>
          </div>
        </article>

        {/* 03 — OPERATING CONSTRAINTS */}

        <article className="incident-section incident-constraints">
          <div className="incident-section-heading">
            <div>
              <span className="incident-section-number">
                03 / OPERATING CONSTRAINTS
              </span>

              <h3>Critical requirements</h3>

              <p>
                Conditions that recovery plans must satisfy.
              </p>
            </div>

            <ShieldCheck size={20} />
          </div>

          <div className="incident-constraint-list">

            <div className="incident-constraint-item">
              <div className="incident-constraint-icon temperature">
                <Thermometer size={19} />
              </div>

              <div className="incident-constraint-copy">
                <span>TEMPERATURE CONTROL</span>
                <strong>{temperature}</strong>

                <p>
                  The medicine requires temperature-controlled
                  transportation.
                </p>
              </div>

              <span className="incident-constraint-tag">
                REQUIRED
              </span>
            </div>

            <div className="incident-constraint-item">
              <div className="incident-constraint-icon deadline">
                <Clock3 size={19} />
              </div>

              <div className="incident-constraint-copy">
                <span>DELIVERY DEADLINE</span>
                <strong>{deadline}</strong>

                <p>
                  Recovery options must be evaluated against
                  the required delivery time.
                </p>
              </div>

              <span className="incident-constraint-tag">
                REQUIRED
              </span>
            </div>

            <div className="incident-constraint-item">
              <div className="incident-constraint-icon approval">
                <CheckCircle2 size={19} />
              </div>

              <div className="incident-constraint-copy">
                <span>DECISION AUTHORITY</span>
                <strong>Human approval</strong>

                <p>
                  A manager reviews the evidence and makes
                  the final decision.
                </p>
              </div>

              <span className="incident-constraint-tag">
                REQUIRED
              </span>
            </div>

          </div>
        </article>

        {/* 04 — OPERATIONAL IMPACT */}

        <article className="incident-section incident-impact">
          <div className="incident-section-heading">
            <div>
              <span className="incident-section-number">
                04 / OPERATIONAL IMPACT
              </span>

              <h3>Impact assessment</h3>

              <p>
                What is known and what remains to be evaluated.
              </p>
            </div>

            <Activity size={20} />
          </div>

          <div className="incident-impact-summary">
            <span>SHIPMENT CONDITION</span>

            <div className="incident-impact-status">
              <span />
              Delivery at risk
            </div>

            <p>
              The road closure may affect the shipment's
              arrival time. Its actual delay has not yet
              been calculated.
            </p>
          </div>

          <div className="incident-unknowns">
            <span className="incident-unknowns-title">
              INFORMATION STILL REQUIRED
            </span>

            <div>
              <span>Revised arrival estimate</span>
              <strong>Pending evaluation</strong>
            </div>

            <div>
              <span>Exact closure location</span>
              <strong>Not provided</strong>
            </div>

            <div>
              <span>Live traffic information</span>
              <strong>Not connected</strong>
            </div>

            <div>
              <span>Alternative route feasibility</span>
              <strong>Pending evaluation</strong>
            </div>
          </div>
        </article>
      </section>

      {/* NEXT WORKFLOW STAGE */}

      <section className="incident-next">
        <div>
          <span className="incident-next-eyebrow">
            NEXT WORKFLOW STAGE
          </span>

          <h3>Recovery plan evaluation</h3>

          <p>
            Compare three recovery strategies for shipment {shipment},
            including their delivery, inventory and compliance impact.
          </p>
        </div>

        <button
          type="button"
          onClick={onContinue}
          className="incident-next-button"
        >
          Continue to Recovery Comparison
          <ArrowRight size={16} />
        </button>
      </section>

      <footer className="dashboard-footer">
        <span>FORESIGHTX INTELLIGENCE SYSTEMS</span>
        <span>
          PROTOTYPE · SIMULATED DATA · HUMAN APPROVAL REQUIRED
        </span>
      </footer>
    </div>
  )
}

export default DisruptionDetails