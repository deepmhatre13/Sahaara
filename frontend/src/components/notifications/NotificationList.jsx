import React from 'react';
import NotificationItem from './NotificationItem';
import EmptyState from '../common/EmptyState';
import { Bell } from 'lucide-react';

export const NotificationList = ({ notifications = [], onMarkAsRead }) => {
  if (!notifications || notifications.length === 0) {
    return <EmptyState icon={Bell} title="No Notifications" description="You have no notifications at this time." />;
  }

  return (
    <div className="space-y-3">
      {notifications.map((n) => (
        <NotificationItem key={n.id} notification={n} onMarkAsRead={onMarkAsRead} />
      ))}
    </div>
  );
};

export default NotificationList;
