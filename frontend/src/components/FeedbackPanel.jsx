const TAG_STYLES = {
  error:   { bg: '#3d1a1a', color: '#f85149' },
  gap:     { bg: '#3a2f0a', color: '#d29922' },
  tip:     { bg: '#1a3a25', color: '#3fb950' },
  concept: { bg: '#2d1f5e', color: '#bc8cff' },
}

function FeedbackItem({ item }) {
  const style = TAG_STYLES[item.tag] || TAG_STYLES.tip
  return (
    <div style={{
      background: '#21262d', border: '1px solid #30363d',
      borderRadius: '8px', padding: '12px 14px', marginBottom: '10px',
    }}>
      <span style={{
        display: 'inline-block', fontSize: '10px', fontWeight: 600,
        padding: '2px 7px', borderRadius: '4px', marginBottom: '6px',
        background: style.bg, color: style.color, textTransform: 'uppercase',
      }}>
        {item.tag}
      </span>
      <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '4px' }}>
        {item.title}
      </div>
      <div style={{ fontSize: '13px', color: '#8b949e', lineHeight: 1.5 }}>
        {item.body}
      </div>
    </div>
  )
}

export default function FeedbackPanel({ result, loading }) {
  if (loading) {
    return (
      <div style={{ padding: '24px', color: '#8b949e', fontSize: '13px' }}>
        <div style={{ marginBottom: '16px' }}>🤖 Analyzing your code…</div>
        {['Checking logic...', 'Scanning patterns...', 'Building feedback...'].map((s) => (
          <div key={s} style={{
            height: '12px', background: '#21262d', borderRadius: '4px',
            marginBottom: '10px', animation: 'pulse 1.5s ease-in-out infinite',
          }} />
        ))}
      </div>
    )
  }

  if (!result) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '100%', padding: '32px',
        color: '#8b949e', textAlign: 'center', gap: '12px',
      }}>
        <span style={{ fontSize: '36px' }}>🤖</span>
        <p style={{ fontSize: '13px', lineHeight: 1.6 }}>
          Write your solution and click <strong style={{ color: '#e6edf3' }}>Analyze Code</strong> for personalized AI feedback.
        </p>
      </div>
    )
  }

  const feedback = result.ai_feedback || {}
  const execResult = result.execution_result || {}

  return (
    <div style={{ padding: '14px', overflowY: 'auto', height: '100%' }}>
      {/* Score row */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
        {[
          { label: 'Code score', value: `${result.score}/100` },
          { label: 'Tests passed', value: `${execResult.passed || 0}/${execResult.total || 0}` },
          { label: 'Verdict', value: result.verdict },
        ].map((card) => (
          <div key={card.label} style={{
            flex: 1, background: '#21262d', borderRadius: '8px',
            padding: '10px', textAlign: 'center',
          }}>
            <div style={{ fontSize: '16px', fontWeight: 600 }}>{card.value}</div>
            <div style={{ fontSize: '11px', color: '#8b949e', marginTop: '2px' }}>{card.label}</div>
          </div>
        ))}
      </div>

      {/* Verdict */}
      {feedback.verdict && (
        <p style={{ fontSize: '13px', color: '#8b949e', marginBottom: '14px', lineHeight: 1.5 }}>
          {feedback.verdict}
        </p>
      )}

      {/* Error / feedback items */}
      {feedback.errors?.length > 0 && (
        <>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
            Feedback
          </div>
          {feedback.errors.map((item, i) => (
            <FeedbackItem key={i} item={item} />
          ))}
        </>
      )}

      {/* Summary / next step */}
      {feedback.summary && (
        <div style={{
          background: '#1a3a25', border: '1px solid #3fb950',
          borderRadius: '8px', padding: '12px 14px', marginTop: '4px',
          fontSize: '13px', color: '#8b949e', lineHeight: 1.6,
        }}>
          <span style={{ color: '#3fb950', fontWeight: 500 }}>Next step: </span>
          {feedback.summary}
        </div>
      )}

      {/* Execution output */}
      {execResult.results?.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
            Test cases
          </div>
          {execResult.results.map((tc) => (
            <div key={tc.test_case} style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              padding: '8px 10px', background: '#21262d',
              borderRadius: '6px', marginBottom: '6px', fontSize: '12px',
            }}>
              <span style={{ color: tc.passed ? '#3fb950' : '#f85149', fontWeight: 600 }}>
                {tc.passed ? '✓' : '✗'}
              </span>
              <span style={{ color: '#8b949e' }}>Test {tc.test_case}</span>
              <span style={{ marginLeft: 'auto', color: tc.passed ? '#3fb950' : '#f85149' }}>
                {tc.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
