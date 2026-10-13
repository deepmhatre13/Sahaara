import client from './client';

export const getCaregivers = async (includeInactive = false) => {
  const response = await client.get('/caregivers', {
    params: { include_inactive: includeInactive },
  });
  return response.data;
};

export const createCaregiver = async (data) => {
  const response = await client.post('/caregivers', data);
  return response.data;
};

export const updateCaregiver = async (caregiverId, data) => {
  const response = await client.patch(`/caregivers/${caregiverId}`, data);
  return response.data;
};

export const deactivateCaregiver = async (caregiverId) => {
  const response = await client.delete(`/caregivers/${caregiverId}`);
  return response.data;
};

