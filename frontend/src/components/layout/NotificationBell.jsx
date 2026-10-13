import React from 'react';
import { Bell } from 'lucide-react';
import { Link } from 'react-router-dom';
import useNotifications from '../../context/NotificationContext';

export const NotificationBell = () => {
  const { unreadCount } = useNotifications();

  return (
    <Link
      to="/notifications"
      className="relative p-2 rounded-xl text-[#1C2733] hover:bg-[#F4F1EC] transition-colors"
      title="Notifications"
    >
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute top-1 right-1 w-4 h-4 bg-[#C0392B] text-white text-[10px] font-black rounded-full flex items-center justify-center border border-white animate-in zoom-in-50 duration-150">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </Link>
  );
};

export default NotificationBell;
