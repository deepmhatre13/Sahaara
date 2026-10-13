import client from './client';

// All auth calls use the existing backend endpoints:
//   POST /api/auth/signup  POST /api/auth/login
//   POST /api/auth/google  GET  /api/auth/me

export const signupApi = async (data) => {
  const response = await client.post('/auth/signup', data);
  return response.data;
};

export const loginApi = async (data) => {
  const response = await client.post('/auth/login', data);
  return response.data;
};

export const googleAuthApi = async (idToken) => {
  // Matches the backend GoogleLoginRequest schema: { id_token }.
  const response = await client.post('/auth/google', { id_token: idToken });
  return response.data;
};

export const getMeApi = async () => {
  const response = await client.get('/auth/me');
  return response.data;
};

