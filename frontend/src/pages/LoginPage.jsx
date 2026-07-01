import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useSkill } from '../context/SkillContext'

export default function LoginPage() {
  const [form, setForm]   = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy]   = useState(false)
  const { login }         = useAuth()
  const { refreshProfile } = useSkill()
  const navigate          = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      await login(form.username, form.password)
      await refreshProfile()
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: '#0f1117',
    }}>
      <div style={{
        width: '380px', background: '#161b22',
        border: '1px solid #30363d', borderRadius: '10px', padding: '32px',
      }}>
        <h1 style={{ fontSize: '20px', marginBottom: '8px', fontWeight: 600 }}>
          ⚡ CodeMentor AI
        </h1>
        <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '24px' }}>
          Sign in to your personalized tutor
        </p>

        {error && (
          <div style={{
            background: '#3d1a1a', border: '1px solid #f85149',
            color: '#f85149', borderRadius: '6px',
            padding: '10px 14px', marginBottom: '16px', fontSize: '13px',
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '14px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#8b949e', marginBottom: '6px' }}>
              Username
            </label>
            <input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="your_username"
              required
            />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#8b949e', marginBottom: '6px' }}>
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            style={{
              width: '100%', padding: '10px',
              background: '#58a6ff', color: '#0f1117',
              fontWeight: 600, fontSize: '14px', borderRadius: '6px',
            }}
          >
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p style={{ marginTop: '20px', fontSize: '13px', color: '#8b949e', textAlign: 'center' }}>
          No account? <Link to="/register" style={{ color: '#58a6ff' }}>Register</Link>
        </p>
      </div>
    </div>
  )
}
