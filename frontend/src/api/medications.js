import client from './client';

export const createMedication = async (data) => {
  const response = await client.post('/medications', data);
  return response.data;
};

export const getMedications = async (userId) => {
  const response = await client.get(`/medications/${userId}`);
  return response.data;
};

export const deleteMedication = async (medicationId) => {
  const response = await client.delete(`/medications/${medicationId}`);
  return response.data;
};

