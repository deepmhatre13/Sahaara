import client from './client';

export const getDashboardData = async (userId) => {
  const response = await client.get(`/dashboard/${userId}`);
  return response.data;
};
