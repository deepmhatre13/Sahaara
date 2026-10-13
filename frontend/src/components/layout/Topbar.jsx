import React from 'react';
import NotificationBell from './NotificationBell';

export const Topbar = ({ title = 'Dashboard Overview' }) => {
  return (
    <header className="bg-white border-b border-[#DDE3E8] px-8 py-4 flex items-center justify-between sticky top-0 z-10">
      <div>
        <h1 className="text-xl font-bold text-[#1C2733]">{title}</h1>
      </div>
      <div className="flex items-center gap-4">
        <NotificationBell />
      </div>
    </header>
  );
};

export default Topbar;
