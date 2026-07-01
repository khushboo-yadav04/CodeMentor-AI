import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useSkill } from '../context/SkillContext'

export default function RegisterPage() {
  const [form, setForm]   = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy]   = useState(false)
  const { register }      = useAuth()
  const { refreshProfile } = useSkill()
  const navigate          = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      await register(form)
      await refreshProfile()
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
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
          Create your account
        </h1>
        <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '24px' }}>
          Start your adaptive coding journey
        </p>

        {error && (
          <div style={{
            background: '#3d1a1a', border: '1px solid #f85149',
            color: '#f85149', borderRadius: '6px',
            padding: '10px 14px', marginBottom: '16px', fontSize: '13px',
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          {['username', 'email', 'password'].map((field) => (
            <div key={field} style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#8b949e', marginBottom: '6px' }}>
                {field.charAt(0).toUpperCase() + field.slice(1)}
              </label>
              <input
                type={field === 'password' ? 'password' : field === 'email' ? 'email' : 'text'}
                value={form[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                required
              />
            </div>
          ))}
          <button
            type="submit"
            disabled={busy}
            style={{
              width: '100%', padding: '10px', marginTop: '6px',
              background: '#58a6ff', color: '#0f1117',
              fontWeight: 600, fontSize: '14px', borderRadius: '6px',
            }}
          >
            {busy ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p style={{ marginTop: '20px', fontSize: '13px', color: '#8b949e', textAlign: 'center' }}>
          Already have an account? <Link to="/login" style={{ color: '#58a6ff' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}
