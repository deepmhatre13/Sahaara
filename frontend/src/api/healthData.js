import client from './client';

export const syncHealthData = async (userId) => {
  const response = await client.post(`/health-data/${userId}/sync`);
  return response.data;
};

export const getHealthSummary = async (userId) => {
  const response = await client.get(`/health-data/${userId}/summary`);
  return response.data;
};

export const getHealthMetrics = async (userId, metricType) => {
  const response = await client.get(`/health-data/${userId}/metrics`, {
    params: { metric_type: metricType },
  });
  return response.data;
};

