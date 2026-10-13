import client from './client';

export const triggerSos = async (data) => {
  const response = await client.post('/sos', data);
  return response.data;
};

export const resolveSosEvent = async (eventId, resolutionNote) => {
  const response = await client.post(`/sos/${eventId}/resolve`, { resolution_note: resolutionNote });
  return response.data;
};

export const getSosHistory = async (userId) => {
  const response = await client.get(`/sos/${userId}`);
  return response.data;
};

