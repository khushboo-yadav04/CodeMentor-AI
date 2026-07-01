import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { problemsAPI, submissionsAPI } from '../utils/api'
import { useSkill } from '../context/SkillContext'
import FeedbackPanel from '../components/FeedbackPanel'
import HintPanel from '../components/HintPanel'

const LANGUAGES = ['python', 'javascript', 'java', 'cpp']
const MONACO_LANG_MAP = { python: 'python', javascript: 'javascript', java: 'java', cpp: 'cpp' }

const DIFF_COLORS = {
  easy:   { bg: '#1a3a25', color: '#3fb950' },
  medium: { bg: '#3a2f0a', color: '#d29922' },
  hard:   { bg: '#3d1a1a', color: '#f85149' },
}

export default function TutorPage() {
  const { problemId } = useParams()
  const navigate = useNavigate()
  const { refreshProfile } = useSkill()

  const [problem, setProblem]     = useState(null)
  const [language, setLanguage]   = useState('python')
  const [code, setCode]           = useState('')
  const [result, setResult]       = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [rightTab, setRightTab]   = useState('feedback') // feedback | hints

  useEffect(() => {
    const load = async () => {
      const res = await problemsAPI.get(problemId)
      setProblem(res.data)
      setCode(res.data.starter_code?.[language] || '')
      setResult(null)
    }
    load()
  }, [problemId])

  const handleLanguageChange = (lang) => {
    setLanguage(lang)
    if (problem) setCode(problem.starter_code?.[lang] || '')
  }

  const getCode = useCallback(() => code, [code])

  const handleAnalyze = async () => {
    if (!code.trim()) return
    setAnalyzing(true)
    setRightTab('feedback')
    try {
      const res = await submissionsAPI.analyze({
        problem_id: Number(problemId),
        language,
        code,
      })
      setResult(res.data)
      await refreshProfile()
    } catch (e) {
      console.error(e)
      alert('Analysis failed. Check that the backend is running and your API key is valid.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (!problem) {
    return <div style={{ padding: '32px', color: '#8b949e' }}>Loading problem…</div>
  }

  const dc = DIFF_COLORS[problem.difficulty] || DIFF_COLORS.medium

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1fr 380px',
      height: 'calc(100vh - 52px)', overflow: 'hidden',
    }}>
      {/* Left: problem + editor */}
      <div style={{ display: 'flex', flexDirection: 'column', borderRight: '1px solid #30363d', overflow: 'hidden' }}>
        {/* Problem panel */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #30363d', background: '#161b22', flexShrink: 0 }}>
          <button
            onClick={() => navigate('/')}
            style={{ background: 'none', color: '#8b949e', fontSize: '12px', marginBottom: '10px', padding: 0 }}
          >
            ← Back to problems
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <h2 style={{ fontSize: '17px', fontWeight: 600 }}>{problem.title}</h2>
            <span style={{
              fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
              background: dc.bg, color: dc.color, fontWeight: 500,
            }}>
              {problem.difficulty}
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#8b949e', lineHeight: 1.6 }}>
            {problem.description}
          </p>
        </div>

        {/* Editor toolbar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '8px 16px', background: '#161b22', borderBottom: '1px solid #30363d', flexShrink: 0,
        }}>
          <select value={language} onChange={(e) => handleLanguageChange(e.target.value)} style={{ width: 'auto' }}>
            {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
          <span style={{ flex: 1 }} />
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            style={{
              padding: '7px 18px', background: '#58a6ff', color: '#0f1117',
              fontWeight: 600, borderRadius: '6px',
            }}
          >
            {analyzing ? 'Analyzing…' : '✨ Analyze Code'}
          </button>
        </div>

        {/* Monaco editor */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <Editor
            height="100%"
            language={MONACO_LANG_MAP[language]}
            value={code}
            onChange={(v) => setCode(v ?? '')}
            theme="vs-dark"
            options={{
              fontSize: 13,
              minimap: { enabled: false },
              automaticLayout: true,
              scrollBeyondLastLine: false,
              padding: { top: 14 },
            }}
          />
        </div>
      </div>

      {/* Right: feedback / hints */}
      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid #30363d', flexShrink: 0 }}>
          {[['feedback', 'Feedback'], ['hints', 'Hints & Ask']].map(([tab, label]) => (
            <button
              key={tab}
              onClick={() => setRightTab(tab)}
              style={{
                flex: 1, padding: '12px', background: 'none',
                color: rightTab === tab ? '#58a6ff' : '#8b949e',
                borderBottom: rightTab === tab ? '2px solid #58a6ff' : '2px solid transparent',
                fontWeight: rightTab === tab ? 600 : 400, fontSize: '13px',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        <div style={{ flex: 1, overflow: 'hidden' }}>
          {rightTab === 'feedback' ? (
            <FeedbackPanel result={result} loading={analyzing} />
          ) : (
            <HintPanel
              problemId={Number(problemId)}
              language={language}
              getCode={getCode}
            />
          )}
        </div>
      </div>
    </div>
  )
}
