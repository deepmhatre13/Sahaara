import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { Bell, Check } from 'lucide-react';

export const NotificationItem = ({ notification, onMarkAsRead }) => {
  const isRead = notification?.is_read || notification?.read;

  return (
    <Card className={`flex items-start justify-between ${isRead ? 'opacity-70' : 'bg-white font-semibold'}`}>
      <div className="flex items-start gap-3 min-w-0">
        <div className={`p-2 rounded-xl mt-0.5 ${isRead ? 'bg-[#F4F1EC] text-[#8A97A5]' : 'bg-[#1E3A5F]/10 text-[#1E3A5F]'}`}>
          <Bell size={18} />
        </div>
        <div className="min-w-0">
          <h4 className="text-sm font-bold text-[#1C2733]">{notification?.title || notification?.message}</h4>
          {notification?.title && <p className="text-xs text-[#8A97A5] mt-0.5">{notification?.message}</p>}
          <p className="text-[10px] text-[#8A97A5] mt-1">{new Date(notification?.created_at || Date.now()).toLocaleString()}</p>
        </div>
      </div>

      {!isRead && (
        <button
          onClick={() => onMarkAsRead?.(notification.id)}
          className="p-1.5 text-[#1E3A5F] hover:bg-[#F4F1EC] rounded-lg transition-colors text-xs flex items-center gap-1 font-bold shrink-0 cursor-pointer"
        >
          <Check size={14} /> Mark Read
        </button>
      )}
    </Card>
  );
};

export default NotificationItem;
