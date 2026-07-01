import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/auth/me'),
}

// ─── Problems ─────────────────────────────────────────────────────────────────
export const problemsAPI = {
  list: (params) => api.get('/problems/', { params }),
  get: (id) => api.get(`/problems/${id}`),
  seed: () => api.post('/problems/seed'),
}

// ─── Submissions ──────────────────────────────────────────────────────────────
export const submissionsAPI = {
  analyze: (data) => api.post('/submissions/analyze', data),
  hint: (data) => api.post('/submissions/hint', data),
  ask: (data) => api.post('/submissions/ask', data),
  history: (limit = 20) => api.get('/submissions/history', { params: { limit } }),
}

// ─── Profile ──────────────────────────────────────────────────────────────────
export const profileAPI = {
  skill: () => api.get('/profile/skill'),
  patterns: () => api.get('/profile/patterns'),
  recommendations: () => api.get('/profile/recommendations'),
  resolvePattern: (id) => api.patch(`/profile/patterns/${id}/resolve`),
}

export default api
