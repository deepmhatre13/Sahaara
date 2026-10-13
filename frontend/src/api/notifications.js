import client from './client';

export const getNotifications = async (userId) => {
  const response = await client.get(`/notifications/${userId}`);
  return response.data;
};

export const markNotificationRead = async (notificationId) => {
  const response = await client.post(`/notifications/${notificationId}/read`);
  return response.data;
};

