import { useState } from 'react'
import { submissionsAPI } from '../utils/api'

export default function HintPanel({ problemId, language, getCode, skillLevel }) {
  const [hints, setHints]       = useState([])
  const [chatHistory, setChat]  = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading]   = useState(false)
  const [mode, setMode]         = useState('hints')  // hints | chat

  const requestHint = async () => {
    setLoading(true)
    try {
      const res = await submissionsAPI.hint({
        problem_id: problemId,
        language,
        code: getCode(),
        hint_number: hints.length + 1,
      })
      setHints((prev) => [res.data, ...prev])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const sendQuestion = async () => {
    if (!question.trim()) return
    const q = question.trim()
    setQuestion('')
    setLoading(true)

    const userMsg = { role: 'user', content: q }
    setChat((prev) => [...prev, userMsg])

    try {
      const res = await submissionsAPI.ask({
        problem_id: problemId,
        language,
        code: getCode(),
        question: q,
        history: chatHistory.slice(-6),
      })
      const aiMsg = {
        role: 'assistant',
        content: res.data.answer,
        followup: res.data.followup,
      }
      setChat((prev) => [...prev, aiMsg])
    } catch (e) {
      setChat((prev) => [...prev, {
        role: 'assistant', content: 'Could not get an answer. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Mode tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #30363d', flexShrink: 0 }}>
        {[['hints', '💡 Hints'], ['chat', '💬 Ask']].map(([m, label]) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            style={{
              flex: 1, padding: '10px', background: 'none',
              color: mode === m ? '#58a6ff' : '#8b949e',
              borderBottom: mode === m ? '2px solid #58a6ff' : '2px solid transparent',
              fontWeight: mode === m ? 600 : 400, fontSize: '13px',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Hints mode */}
      {mode === 'hints' && (
        <>
          <div style={{ flex: 1, overflowY: 'auto', padding: '14px' }}>
            {hints.length === 0 && (
              <div style={{ color: '#8b949e', fontSize: '13px', textAlign: 'center', padding: '32px 16px' }}>
                <p style={{ marginBottom: '8px' }}>Stuck? Get a Socratic hint.</p>
                <p style={{ fontSize: '12px' }}>Hints get more specific with each request.</p>
              </div>
            )}
            {hints.map((h, i) => (
              <div key={i} style={{
                background: '#21262d', border: '1px solid #30363d',
                borderRadius: '8px', padding: '12px 14px', marginBottom: '10px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{
                    fontSize: '10px', fontWeight: 600, padding: '2px 7px',
                    borderRadius: '4px', background: '#2d1f5e', color: '#bc8cff',
                    textTransform: 'uppercase',
                  }}>
                    hint {h.hint_number}
                  </span>
                  <span style={{ fontSize: '12px', color: '#8b949e' }}>{h.concept}</span>
                </div>
                <p style={{ fontSize: '13px', color: '#e6edf3', marginBottom: '8px', lineHeight: 1.5 }}>
                  {h.hint}
                </p>
                <p style={{ fontSize: '12px', color: '#58a6ff', fontStyle: 'italic' }}>
                  {h.question}
                </p>
              </div>
            ))}
          </div>
          <div style={{ padding: '12px', borderTop: '1px solid #30363d', flexShrink: 0 }}>
            <button
              onClick={requestHint}
              disabled={loading}
              style={{
                width: '100%', padding: '9px',
                background: '#21262d', border: '1px solid #30363d',
                color: '#e6edf3', borderRadius: '6px', fontWeight: 500,
              }}
            >
              {loading ? 'Generating hint…' : `Get hint ${hints.length + 1}`}
            </button>
          </div>
        </>
      )}

      {/* Chat mode */}
      {mode === 'chat' && (
        <>
          <div style={{ flex: 1, overflowY: 'auto', padding: '14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {chatHistory.length === 0 && (
              <div style={{ color: '#8b949e', fontSize: '13px', textAlign: 'center', padding: '32px 16px' }}>
                Ask anything about the problem, concepts, or your code.
              </div>
            )}
            {chatHistory.map((msg, i) => (
              <div key={i} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '90%' }}>
                <div style={{
                  padding: '10px 14px', borderRadius: '8px', fontSize: '13px', lineHeight: 1.5,
                  background: msg.role === 'user' ? '#1f3a5f' : '#21262d',
                  color: msg.role === 'user' ? '#58a6ff' : '#e6edf3',
                  border: '1px solid #30363d',
                }}>
                  {msg.content}
                </div>
                {msg.followup && (
                  <div style={{ fontSize: '12px', color: '#58a6ff', fontStyle: 'italic', marginTop: '4px', paddingLeft: '4px' }}>
                    {msg.followup}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', color: '#8b949e', fontSize: '13px', padding: '4px' }}>
                Thinking…
              </div>
            )}
          </div>
          <div style={{ padding: '12px', borderTop: '1px solid #30363d', display: 'flex', gap: '8px', flexShrink: 0 }}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendQuestion()}
              placeholder="Ask about your code…"
              disabled={loading}
              style={{ flex: 1 }}
            />
            <button
              onClick={sendQuestion}
              disabled={loading || !question.trim()}
              style={{
                padding: '8px 14px', background: '#58a6ff',
                color: '#0f1117', fontWeight: 600, borderRadius: '6px',
                flexShrink: 0,
              }}
            >
              →
            </button>
          </div>
        </>
      )}
    </div>
  )
}
