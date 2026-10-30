import { useState, type FormEvent } from 'react'
import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from 'lucide-react'

import Dashboard from './dashboard'
import './App.css'

type AuthMode = 'signin' | 'signup'

function App() {
  const [mode, setMode] = useState<AuthMode>('signin')
  const [showPassword, setShowPassword] = useState(false)
  const [notice, setNotice] = useState('')
  const [showDashboard, setShowDashboard] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (mode === 'signin') {
      setNotice('')
      setShowDashboard(true)
    } else {
      setNotice(
        'Registration is a frontend prototype. Backend authentication is not connected yet.'
      )
    }
  }

  function changeMode(nextMode: AuthMode) {
    setMode(nextMode)
    setNotice('')
    setShowPassword(false)
  }

  if (showDashboard) {
    return (
      <Dashboard
        onSignOut={() => {
          setShowDashboard(false)
          setMode('signin')
          setNotice('')
        }}
      />
    )
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <div className="auth-heading">
          <span className="auth-eyebrow">SECURE WORKSPACE</span>

          <h1>
            {mode === 'signin'
              ? 'Welcome back.'
              : 'Create your account.'}
          </h1>

          <p>
            {mode === 'signin'
              ? 'Sign in to access your workspace.'
              : 'Create an account to access your workspace.'}
          </p>
        </div>

        <div
          className="auth-mode-switch"
          role="tablist"
          aria-label="Account access"
        >
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'signin'}
            className={
              mode === 'signin'
                ? 'auth-tab active-tab'
                : 'auth-tab'
            }
            onClick={() => changeMode('signin')}
          >
            Sign in
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={mode === 'signup'}
            className={
              mode === 'signup'
                ? 'auth-tab active-tab'
                : 'auth-tab'
            }
            onClick={() => changeMode('signup')}
          >
            Create account
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === 'signup' && (
            <div className="form-field">
              <label htmlFor="fullName">Full name</label>

              <input
                id="fullName"
                name="fullName"
                type="text"
                placeholder="Enter your full name"
                autoComplete="name"
                required
              />
            </div>
          )}

          <div className="form-field">
            <label htmlFor="email">Email address</label>

            <div className="input-wrapper">
              <Mail size={18} aria-hidden="true" />

              <input
                id="email"
                name="email"
                type="email"
                placeholder="name@company.com"
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>

            <div className="input-wrapper">
              <LockKeyhole size={18} aria-hidden="true" />

              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                autoComplete={
                  mode === 'signin'
                    ? 'current-password'
                    : 'new-password'
                }
                minLength={8}
                required
              />

              <button
                type="button"
                className="password-toggle"
                aria-label={
                  showPassword
                    ? 'Hide password'
                    : 'Show password'
                }
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          {mode === 'signin' && (
            <div className="forgot-row">
              <button
                type="button"
                className="forgot-button"
                onClick={() =>
                  setNotice(
                    'Password recovery will be connected with backend authentication.'
                  )
                }
              >
                Forgot password?
              </button>
            </div>
          )}

          {mode === 'signup' && (
            <p className="password-hint">
              Use at least 8 characters for your password.
            </p>
          )}

          <button type="submit" className="auth-submit">
            <span>
              {mode === 'signin'
                ? 'Sign in to workspace'
                : 'Create account'}
            </span>

            <ArrowRight size={18} />
          </button>
        </form>

        {notice && (
          <div className="auth-notice" role="status">
            {notice}
          </div>
        )}

        <div className="auth-security">
          <ShieldCheck size={17} />
          <span>Secure workspace access</span>
        </div>
      </section>
    </main>
  )
}

export default App