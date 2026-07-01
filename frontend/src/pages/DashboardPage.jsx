import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { problemsAPI } from '../utils/api'
import { useSkill } from '../context/SkillContext'
import { useAuth } from '../context/AuthContext'

const DIFF_COLORS = {
  easy:   { bg: '#1a3a25', color: '#3fb950', border: '#3fb950' },
  medium: { bg: '#3a2f0a', color: '#d29922', border: '#d29922' },
  hard:   { bg: '#3d1a1a', color: '#f85149', border: '#f85149' },
}

function ProblemCard({ problem, onClick }) {
  const dc = DIFF_COLORS[problem.difficulty] || DIFF_COLORS.medium
  return (
    <div
      onClick={onClick}
      style={{
        background: '#161b22', border: '1px solid #30363d',
        borderRadius: '10px', padding: '18px 20px',
        cursor: 'pointer', transition: 'border-color 0.15s',
      }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = '#58a6ff'}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = '#30363d'}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
        <span style={{ fontWeight: 600, fontSize: '15px' }}>{problem.title}</span>
        <span style={{
          fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
          background: dc.bg, color: dc.color, border: `1px solid ${dc.border}`,
          fontWeight: 500,
        }}>
          {problem.difficulty}
        </span>
      </div>
      <p style={{ color: '#8b949e', fontSize: '13px', lineHeight: 1.5, marginBottom: '12px' }}>
        {problem.description.slice(0, 120)}…
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {(problem.tags || []).map((t) => (
          <span key={t} style={{
            fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
            background: '#1f3a5f', color: '#58a6ff',
          }}>{t}</span>
        ))}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const [problems, setProblems] = useState([])
  const [loading, setLoading]   = useState(true)
  const [filter, setFilter]     = useState('all')
  const { profile, recommendations, refreshProfile } = useSkill()
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const init = async () => {
      try {
        await problemsAPI.seed()   // idempotent — no-op if already seeded
      } catch (_) {}
      const res = await problemsAPI.list()
      setProblems(res.data)
      await refreshProfile()
      setLoading(false)
    }
    init()
  }, [])

  const filtered = filter === 'all'
    ? problems
    : problems.filter((p) => p.difficulty === filter)

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: 600, marginBottom: '6px' }}>
          Welcome back, {user?.username} 👋
        </h1>
        <p style={{ color: '#8b949e' }}>
          {profile
            ? `You're at ${profile.level} level — ${profile.overall_score.toFixed(0)}/100 skill score`
            : 'Pick a problem to start coding'}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '24px' }}>
        {/* Problem list */}
        <div>
          {/* Filter tabs */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {['all', 'easy', 'medium', 'hard'].map((d) => (
              <button
                key={d}
                onClick={() => setFilter(d)}
                style={{
                  padding: '6px 16px', borderRadius: '6px',
                  background: filter === d ? '#58a6ff' : '#21262d',
                  color: filter === d ? '#0f1117' : '#8b949e',
                  border: '1px solid #30363d',
                  fontWeight: filter === d ? 600 : 400,
                }}
              >
                {d.charAt(0).toUpperCase() + d.slice(1)}
              </button>
            ))}
          </div>

          {loading ? (
            <p style={{ color: '#8b949e' }}>Loading problems…</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {filtered.map((p) => (
                <ProblemCard
                  key={p.id}
                  problem={p}
                  onClick={() => navigate(`/tutor/${p.id}`)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div>
          {/* Skill radar */}
          {profile && (
            <div style={{
              background: '#161b22', border: '1px solid #30363d',
              borderRadius: '10px', padding: '18px', marginBottom: '16px',
            }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '14px' }}>
                Skill Breakdown
              </h3>
              {[
                ['Arrays', profile.arrays],
                ['Strings', profile.strings],
                ['Hash Maps', profile.hashmaps],
                ['Recursion', profile.recursion],
                ['DP', profile.dynamic_programming],
                ['Trees', profile.trees],
                ['Sorting', profile.sorting],
                ['Binary Search', profile.binary_search],
              ].map(([label, score]) => (
                <div key={label} style={{ marginBottom: '9px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '12px', color: '#8b949e' }}>{label}</span>
                    <span style={{ fontSize: '12px', color: '#e6edf3' }}>{score.toFixed(0)}</span>
                  </div>
                  <div style={{ height: '4px', background: '#30363d', borderRadius: '2px' }}>
                    <div style={{
                      height: '100%', borderRadius: '2px',
                      width: `${score}%`,
                      background: score < 30 ? '#f85149' : score < 60 ? '#d29922' : '#3fb950',
                      transition: 'width 0.4s',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div style={{
              background: '#161b22', border: '1px solid #30363d',
              borderRadius: '10px', padding: '18px',
            }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '14px' }}>
                Recommended for you
              </h3>
              {recommendations.map((r, i) => (
                <div key={i} style={{
                  padding: '10px', background: '#21262d', borderRadius: '6px',
                  marginBottom: '8px',
                }}>
                  <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '3px' }}>
                    {r.concept}
                  </div>
                  <div style={{ fontSize: '12px', color: '#8b949e' }}>{r.reason}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
