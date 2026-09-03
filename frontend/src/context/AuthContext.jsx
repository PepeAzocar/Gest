import { createContext, useContext, useEffect, useState } from 'react'
import { api, getToken, setToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    api
      .get('/auth/me')
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false))
  }, [])

  async function login(username, password) {
    const { access_token } = await api.login(username, password)
    setToken(access_token)
    const me = await api.get('/auth/me')
    setUser(me)
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  function hasRole(...roles) {
    if (!user) return false
    return user.roles.some((r) => roles.includes(r.code))
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
