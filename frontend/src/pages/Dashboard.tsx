import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { Link, Navigate } from 'react-router-dom'

export function Dashboard() {
  const { user, logout } = useAuth()
  const [projects, setProjects] = useState<any[]>([])
  const [bugs, setBugs] = useState<any[]>([])

  useEffect(() => {
    async function fetchData() {
      const [p, b] = await Promise.all([
        api.get('/projects/'),
        api.get('/bugs/'),
      ])
      setProjects(p.data)
      setBugs(b.data)
    }
    if (user) fetchData()
  }, [user])

  if (!user) return <Navigate to="/login" replace />

  return (
      <div style={{ display: 'grid', gap: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Welcome, {user.username} ({user.user_type})</h2>
          <button onClick={logout}>Logout</button>
        </div>
        <section>
          <h3>Projects</h3>
          <ul>
            {projects.map(p => (
              <li key={p.id}>{p.name}</li>
            ))}
          </ul>
        </section>
        <section>
          <h3>Bugs</h3>
          <ul>
            {bugs.map(b => (
              <li key={b.id}>{b.title} - {b.status}</li>
            ))}
          </ul>
        </section>
      </div>
  )
}
