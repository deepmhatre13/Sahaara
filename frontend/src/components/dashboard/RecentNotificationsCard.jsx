import React from 'react';
import Card from '../common/Card';
import { Bell, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const RecentNotificationsCard = ({ notifications = [] }) => {
  const recent = (notifications || []).slice(0, 3);

  return (
    <Card className="flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-lg text-[#1C2733]">Recent Notifications</h3>
          <Link to="/notifications" className="text-xs font-semibold text-[#1E3A5F] hover:underline flex items-center">
            View All <ChevronRight size={14} />
          </Link>
        </div>

        {recent.length === 0 ? (
          <p className="text-sm text-[#8A97A5] text-center py-6">No recent notifications</p>
        ) : (
          <div className="space-y-2.5">
            {recent.map((n) => (
              <div key={n.id} className="p-3 bg-[#F4F1EC]/60 rounded-xl flex items-start gap-3 border border-[#DDE3E8]/50">
                <div className="p-2 bg-[#1E3A5F]/10 text-[#1E3A5F] rounded-lg mt-0.5">
                  <Bell size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold text-[#1C2733] truncate">{n.title || n.message}</p>
                  {n.title && <p className="text-xs text-[#8A97A5] truncate">{n.message}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default RecentNotificationsCard;
