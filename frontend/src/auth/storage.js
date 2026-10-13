/**
 * Single source of truth for auth persistence keys.
 *
 * The whole frontend (API client interceptor + AuthContext) uses exactly one
 * token key and one user key. Do not introduce additional competing keys.
 */
export const TOKEN_STORAGE_KEY = 'sahaara_token';
export const USER_STORAGE_KEY = 'sahaara_user';

export const getStoredToken = () => localStorage.getItem(TOKEN_STORAGE_KEY);

export const setStoredToken = (token) => {
  if (token) localStorage.setItem(TOKEN_STORAGE_KEY, token);
  else localStorage.removeItem(TOKEN_STORAGE_KEY);
};

export const clearStoredAuth = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};