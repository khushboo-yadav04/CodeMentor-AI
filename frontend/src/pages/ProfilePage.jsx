import { useEffect, useState } from 'react'
import { useSkill } from '../context/SkillContext'
import { submissionsAPI } from '../utils/api'

const SEV_COLORS = { high: '#f85149', med: '#d29922', low: '#3fb950' }

export default function ProfilePage() {
  const { profile, patterns, recommendations, refreshProfile } = useSkill()
  const [history, setHistory] = useState([])

  useEffect(() => {
    refreshProfile()
    submissionsAPI.history(15).then((r) => setHistory(r.data)).catch(() => {})
  }, [])

  if (!profile) {
    return <div style={{ padding: '32px', color: '#8b949e' }}>Loading profile…</div>
  }

  const concepts = [
    ['Arrays', profile.arrays],
    ['Strings', profile.strings],
    ['Hash Maps', profile.hashmaps],
    ['Recursion', profile.recursion],
    ['Dynamic Programming', profile.dynamic_programming],
    ['Trees', profile.trees],
    ['Graphs', profile.graphs],
    ['Sorting', profile.sorting],
    ['Two Pointers', profile.two_pointers],
    ['Binary Search', profile.binary_search],
  ]

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '32px 24px' }}>
      <h1 style={{ fontSize: '22px', fontWeight: 600, marginBottom: '24px' }}>
        Your Learning Profile
      </h1>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '28px' }}>
        <div style={{ flex: 1, background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#58a6ff' }}>
            {profile.overall_score.toFixed(0)}
          </div>
          <div style={{ fontSize: '12px', color: '#8b949e', marginTop: '4px' }}>Overall Skill Score</div>
        </div>
        <div style={{ flex: 1, background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#bc8cff', textTransform: 'capitalize' }}>
            {profile.level}
          </div>
          <div style={{ fontSize: '12px', color: '#8b949e', marginTop: '4px' }}>Current Level</div>
        </div>
        <div style={{ flex: 1, background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#3fb950' }}>
            {history.length}
          </div>
          <div style={{ fontSize: '12px', color: '#8b949e', marginTop: '4px' }}>Submissions</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Concept Mastery</h3>
          {concepts.map(([label, score]) => (
            <div key={label} style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span style={{ fontSize: '13px' }}>{label}</span>
                <span style={{ fontSize: '12px', color: '#8b949e' }}>{score.toFixed(0)}/100</span>
              </div>
              <div style={{ height: '6px', background: '#30363d', borderRadius: '3px' }}>
                <div style={{
                  height: '100%', borderRadius: '3px', width: `${score}%`,
                  background: score < 30 ? '#f85149' : score < 60 ? '#d29922' : '#3fb950',
                  transition: 'width 0.4s',
                }} />
              </div>
            </div>
          ))}
        </div>

        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Recurring Error Patterns</h3>
          {patterns.length === 0 ? (
            <p style={{ fontSize: '13px', color: '#8b949e' }}>
              No recurring patterns detected yet. Keep submitting code!
            </p>
          ) : (
            patterns.map((p) => (
              <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 0', borderBottom: '1px solid #21262d' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: SEV_COLORS[p.severity] || SEV_COLORS.med, flexShrink: 0 }} />
                <span style={{ fontSize: '13px', flex: 1 }}>{p.pattern_name}</span>
                <span style={{ fontSize: '12px', color: '#8b949e' }}>{p.occurrences}×</span>
              </div>
            ))
          )}
        </div>
      </div>

      {recommendations.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', marginTop: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Recommended Practice Areas</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
            {recommendations.map((r, i) => (
              <div key={i} style={{ padding: '12px 14px', background: '#21262d', borderRadius: '8px' }}>
                <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '4px' }}>{r.concept}</div>
                <div style={{ fontSize: '12px', color: '#8b949e' }}>{r.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', marginTop: '20px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Recent Submissions</h3>
        {history.length === 0 ? (
          <p style={{ fontSize: '13px', color: '#8b949e' }}>No submissions yet.</p>
        ) : (
          history.map((s) => (
            <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 0', borderBottom: '1px solid #21262d', fontSize: '13px' }}>
              <span style={{ color: s.verdict === 'accepted' ? '#3fb950' : s.verdict === 'partial' ? '#d29922' : '#f85149', fontWeight: 600, width: '90px' }}>
                {s.verdict}
              </span>
              <span style={{ color: '#8b949e', width: '90px' }}>{s.language}</span>
              <span style={{ flex: 1 }}>Score: {s.score}/100</span>
              <span style={{ color: '#8b949e', fontSize: '12px' }}>
                {new Date(s.submitted_at).toLocaleDateString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
