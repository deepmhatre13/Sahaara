import React from 'react';
import useNotifications from '../hooks/useNotifications';
import NotificationList from '../components/notifications/NotificationList';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';

export const NotificationsPage = () => {
  const { notifications, unreadCount, loading, markAsRead, refetch } = useNotifications();

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#DDE3E8]">
        <div>
          <h2 className="text-2xl font-bold text-[#1C2733]">Notification Center</h2>
          <p className="text-sm text-[#8A97A5] mt-0.5">
            {unreadCount > 0 ? `You have ${unreadCount} unread care alert(s)` : 'All system and care alerts'}
          </p>
        </div>
        <Button variant="secondary" onClick={refetch} className="self-start sm:self-auto">
          Refresh List
        </Button>
      </div>

      {/* Notifications Full List */}
      {loading && notifications.length === 0 ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <NotificationList notifications={notifications} onMarkRead={markAsRead} />
      )}
    </div>
  );
};

export default NotificationsPage;
