import client from './client';

export const uploadReport = async (userId, file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await client.post(`/reports/${userId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getReports = async (userId) => {
  const response = await client.get(`/reports/${userId}`);
  return response.data;
};

