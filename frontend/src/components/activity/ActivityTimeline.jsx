import React from 'react';
import Card from '../common/Card';
import { Clock, Activity, AlertTriangle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const ActivityTimeline = ({ events = [] }) => {
  const getEventIcon = (type) => {
    switch (type) {
      case 'MOTION_DETECTED':
        return { icon: Activity, color: 'text-[#2E8B57]', bg: 'bg-emerald-100' };
      case 'NO_MOTION':
        return { icon: Clock, color: 'text-[#E8A33D]', bg: 'bg-amber-100' };
      case 'INACTIVITY_THRESHOLD_EXCEEDED':
        return { icon: AlertTriangle, color: 'text-[#C0392B]', bg: 'bg-red-100' };
      default:
        return { icon: Activity, color: 'text-[#1E3A5F]', bg: 'bg-blue-100' };
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-[#1C2733] mb-6">Activity Timeline Log</h3>
      {events.length === 0 ? (
        <p className="text-sm text-[#8A97A5] text-center py-6">No recent activity events recorded.</p>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#DDE3E8]">
          {events.map((evt, idx) => {
            const { icon: Icon, color, bg } = getEventIcon(evt.event_type || evt.type);
            return (
              <div key={evt.id || idx} className="relative flex items-start gap-4">
                <div
                  className={`absolute -left-6 top-0 w-6 h-6 rounded-full ${bg} ${color} flex items-center justify-center border-2 border-white shadow-xs`}
                >
                  <Icon size={14} />
                </div>
                <div className="flex-1 bg-[#F4F1EC]/60 p-4 rounded-xl border border-[#DDE3E8]/50">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-[#1C2733]">
                      {evt.event_type || evt.type || 'Motion Activity'}
                    </span>
                    <span className="text-xs text-[#8A97A5]">
                      {evt.created_at || evt.timestamp
                        ? formatDistanceToNow(new Date(evt.created_at || evt.timestamp), { addSuffix: true })
                        : 'Recently'}
                    </span>
                  </div>
                  {evt.description && <p className="text-xs text-[#8A97A5] mt-1">{evt.description}</p>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};

export default ActivityTimeline;

