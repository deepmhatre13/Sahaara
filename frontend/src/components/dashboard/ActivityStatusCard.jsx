import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { Activity } from 'lucide-react';

export const ActivityStatusCard = ({ statusData }) => {
  const status = statusData?.current_status || 'Normal Motion';
  const lastActive = statusData?.last_active || 'Just now';

  return (
    <Card title="Activity Monitor">
      <div className="flex flex-col items-center justify-center py-6 text-center">
        <div className="p-4 bg-emerald-50 text-emerald-600 rounded-full mb-3">
          <Activity size={32} />
        </div>
        <Badge variant="success" size="lg" className="mb-2">
          {status}
        </Badge>
        <p className="text-xs text-[#8A97A5] mt-1">Last activity detected: {lastActive}</p>
      </div>
    </Card>
  );
};

export default ActivityStatusCard;
