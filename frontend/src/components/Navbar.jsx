import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useSkill } from '../context/SkillContext'

const styles = {
  nav: {
    display: 'flex', alignItems: 'center', gap: '16px',
    padding: '0 24px', height: '52px',
    background: '#161b22', borderBottom: '1px solid #30363d',
    position: 'sticky', top: 0, zIndex: 100,
  },
  logo: { fontWeight: 600, fontSize: '15px', color: '#58a6ff', textDecoration: 'none' },
  spacer: { flex: 1 },
  link: { color: '#8b949e', textDecoration: 'none', fontSize: '13px' },
  levelBadge: {
    padding: '3px 10px', borderRadius: '12px',
    background: '#1f3a5f', color: '#58a6ff',
    fontSize: '12px', fontWeight: 500,
  },
  skillBar: { display: 'flex', alignItems: 'center', gap: '8px' },
  barTrack: { width: '80px', height: '5px', background: '#30363d', borderRadius: '3px' },
  logoutBtn: {
    padding: '5px 12px', background: 'transparent',
    border: '1px solid #30363d', color: '#8b949e', borderRadius: '6px',
    fontSize: '12px',
  },
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const { profile } = useSkill()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>⚡ CodeMentor AI</Link>
      <Link to="/" style={styles.link}>Problems</Link>
      <Link to="/profile" style={styles.link}>Profile</Link>
      <div style={styles.spacer} />
      {profile && (
        <div style={styles.skillBar}>
          <span style={{ fontSize: '12px', color: '#8b949e' }}>Skill</span>
          <div style={styles.barTrack}>
            <div style={{
              height: '100%', borderRadius: '3px',
              width: `${profile.overall_score}%`,
              background: '#58a6ff', transition: 'width 0.4s',
            }} />
          </div>
          <span style={styles.levelBadge}>{profile.level}</span>
        </div>
      )}
      <span style={{ fontSize: '13px', color: '#8b949e' }}>{user?.username}</span>
      <button style={styles.logoutBtn} onClick={handleLogout}>Logout</button>
    </nav>
  )
}
