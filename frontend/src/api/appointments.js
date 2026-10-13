import client from './client';

export const createAppointment = async (data) => {
  const response = await client.post('/appointments', data);
  return response.data;
};

export const getAppointments = async (userId) => {
  const response = await client.get(`/appointments/${userId}`);
  return response.data;
};

export const deleteAppointment = async (appointmentId) => {
  const response = await client.delete(`/appointments/${appointmentId}`);
  return response.data;
};

