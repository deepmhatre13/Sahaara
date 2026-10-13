import client from './client';

export const startMonitoring = async (userId) => {
  const response = await client.post(`/activity/${userId}/start-monitoring`);
  return response.data;
};

export const getActivityStatus = async (userId) => {
  const response = await client.get(`/activity/${userId}/status`);
  return response.data;
};

export const getActivityEvents = async (userId) => {
  const response = await client.get(`/activity/${userId}/events`);
  return response.data;
};

