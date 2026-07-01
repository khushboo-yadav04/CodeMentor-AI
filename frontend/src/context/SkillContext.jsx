import { createContext, useContext, useState, useCallback } from 'react'
import { profileAPI } from '../utils/api'

const SkillContext = createContext(null)

export function SkillProvider({ children }) {
  const [profile, setProfile] = useState(null)
  const [patterns, setPatterns] = useState([])
  const [recommendations, setRecommendations] = useState([])

  const refreshProfile = useCallback(async () => {
    try {
      const [skillRes, patRes, recRes] = await Promise.all([
        profileAPI.skill(),
        profileAPI.patterns(),
        profileAPI.recommendations(),
      ])
      setProfile(skillRes.data)
      setPatterns(patRes.data)
      setRecommendations(recRes.data)
    } catch (e) {
      // Not logged in yet — silent fail
    }
  }, [])

  return (
    <SkillContext.Provider value={{ profile, patterns, recommendations, refreshProfile }}>
      {children}
    </SkillContext.Provider>
  )
}

export const useSkill = () => useContext(SkillContext)
