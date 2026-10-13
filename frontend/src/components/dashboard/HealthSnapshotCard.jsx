import React from 'react';
import Card from '../common/Card';
import SyncHealthDataButton from '../health/SyncHealthDataButton';
import { Heart, Activity } from 'lucide-react';

export const HealthSnapshotCard = ({ summary, onSyncSuccess }) => {
  return (
    <Card
      title="Health Snapshot"
      action={<SyncHealthDataButton onSyncSuccess={onSyncSuccess} />}
    >
      <div className="space-y-4 py-2">
        <div className="flex items-center justify-between p-3 bg-[#F4F1EC]/60 rounded-xl">
          <div className="flex items-center gap-3">
            <Heart size={18} className="text-rose-500" />
            <span className="text-sm font-semibold text-[#1C2733]">Heart Rate</span>
          </div>
          <span className="text-sm font-bold text-[#1C2733]">{summary?.heart_rate || 72} BPM</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-[#F4F1EC]/60 rounded-xl">
          <div className="flex items-center gap-3">
            <Activity size={18} className="text-sky-500" />
            <span className="text-sm font-semibold text-[#1C2733]">Blood Oxygen</span>
          </div>
          <span className="text-sm font-bold text-[#1C2733]">{summary?.spo2 || 98}%</span>
        </div>
      </div>
    </Card>
  );
};

export default HealthSnapshotCard;
