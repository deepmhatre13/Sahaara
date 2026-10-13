import React, { createContext, useState, useCallback, useContext } from 'react';
import { getNotifications, markNotificationRead as markReadApi } from '../api/notifications';
import useAuth from '../hooks/useAuth';
import usePolling from '../hooks/usePolling';

export const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated || !user?.id) return;
    try {
      setLoading(true);
      const data = await getNotifications(user.id);
      setNotifications(data || []);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user?.id]);

  // Poll notifications every 25 seconds
  usePolling(fetchNotifications, 25000, isAuthenticated && !!user?.id);

  const markAsRead = async (notificationId) => {
    try {
      await markReadApi(notificationId);
      setNotifications((prev) =>
        prev.map((item) =>
          item.id === notificationId ? { ...item, is_read: true, read: true } : item
        )
      );
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read && !n.read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        refetch: fetchNotifications,
        markAsRead,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export default useNotifications;
