import React, { createContext, useState, useEffect } from 'react';
import { loginApi, signupApi, googleAuthApi, getMeApi } from '../api/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('sahaara_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('sahaara_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await getMeApi();
          // Fix: Backend GET /api/auth/me directly returns the user object (MeResponse), not { user: ... }
          const finalUser = userData.user || userData;
          setUser(finalUser);
          localStorage.setItem('sahaara_user', JSON.stringify(finalUser));
        } catch (err) {
          console.error("Token verification failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const saveAuthData = (data) => {
    const { access_token, user: userData } = data;
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('sahaara_token', access_token);
    localStorage.setItem('sahaara_user', JSON.stringify(userData));
  };

  const login = async (email, password) => {
    const data = await loginApi({ email, password });
    saveAuthData(data);
    return data;
  };

  const signup = async (fullName, email, password) => {
    const data = await signupApi({ full_name: fullName, email, password });
    saveAuthData(data);
    return data;
  };

  const loginWithGoogle = async (idToken) => {
    const data = await googleAuthApi(idToken);
    saveAuthData(data);
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('sahaara_token');
    localStorage.removeItem('sahaara_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        signup,
        loginWithGoogle,
        logout,
        isAuthenticated: !!token && !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

