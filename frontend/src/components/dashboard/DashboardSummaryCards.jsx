import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { Activity, Heart, Moon } from 'lucide-react';

export const DashboardSummaryCards = ({ data }) => {
  const activityStatus = data?.activity_status?.current_status || 'Active';
  const heartRate = data?.health_summary?.heart_rate || 72;
  const spo2 = data?.health_summary?.spo2 || 98;
  const sleepHours = data?.health_summary?.sleep_hours || 7.5;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="flex items-center gap-4">
        <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
          <Activity size={24} />
        </div>
        <div>
          <p className="text-xs font-semibold text-[#8A97A5] uppercase tracking-wider">Status</p>
          <p className="text-lg font-bold text-[#1C2733] mt-0.5">{activityStatus}</p>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
          <Heart size={24} />
        </div>
        <div>
          <p className="text-xs font-semibold text-[#8A97A5] uppercase tracking-wider">Heart Rate</p>
          <p className="text-lg font-bold text-[#1C2733] mt-0.5">{heartRate} BPM</p>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="p-3 bg-sky-50 text-sky-600 rounded-xl">
          <Activity size={24} />
        </div>
        <div>
          <p className="text-xs font-semibold text-[#8A97A5] uppercase tracking-wider">Blood Oxygen</p>
          <p className="text-lg font-bold text-[#1C2733] mt-0.5">{spo2}%</p>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
          <Moon size={24} />
        </div>
        <div>
          <p className="text-xs font-semibold text-[#8A97A5] uppercase tracking-wider">Sleep</p>
          <p className="text-lg font-bold text-[#1C2733] mt-0.5">{sleepHours} hrs</p>
        </div>
      </Card>
    </div>
  );
};

export default DashboardSummaryCards;
