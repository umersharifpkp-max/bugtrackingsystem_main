import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

export function RegisterPage() {
  const { register, user } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [userType, setUserType] = useState<'manager'|'qa'|'developer'>('qa')
  const [error, setError] = useState<string | null>(null)

  if (user) return <Navigate to="/" replace />

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await register({ email, password, user_type: userType })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Register failed')
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ display: 'grid', gap: 8, maxWidth: 360 }}>
      <h2>Register</h2>
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <select value={userType} onChange={e => setUserType(e.target.value as any)}>
        <option value="manager">Manager</option>
        <option value="qa">QA</option>
        <option value="developer">Developer</option>
      </select>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit">Create account</button>
    </form>
  )
}
