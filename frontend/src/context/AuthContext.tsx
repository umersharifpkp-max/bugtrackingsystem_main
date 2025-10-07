import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../lib/api';

export type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  user_type: 'manager' | 'qa' | 'developer';
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: { email: string; password: string; first_name?: string; last_name?: string; user_type: User['user_type'] }) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access');
    async function fetchMe() {
      try {
        if (token) {
          const { data } = await api.get<User>('/auth/me/');
          setUser(data);
        }
      } catch (e) {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
      } finally {
        setLoading(false);
      }
    }
    fetchMe();
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post<{ access: string; refresh: string }>('/auth/login/', { username: email, password });
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    const me = await api.get<User>('/auth/me/');
    setUser(me.data);
  };

  const register = async (payload: { email: string; password: string; first_name?: string; last_name?: string; user_type: User['user_type'] }) => {
    await api.post('/auth/register/', { ...payload, username: payload.email });
    await login(payload.email, payload.password);
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh');
    try {
      if (refresh) {
        await api.post('/auth/logout/', { refresh });
      }
    } finally {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      setUser(null);
    }
  };

  const value = useMemo(() => ({ user, loading, login, register, logout }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
