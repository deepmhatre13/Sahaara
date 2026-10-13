import React from 'react';
import Card from '../common/Card';
import { Heart, Activity, Moon, Footprints } from 'lucide-react';

export const HealthMetricCard = ({ title, value, unit, icon: Icon, color = 'text-[#1E3A5F]' }) => {
  return (
    <Card className="flex items-center gap-4">
      {Icon && (
        <div className={`p-3.5 bg-[#F4F1EC] rounded-2xl ${color}`}>
          <Icon size={24} />
        </div>
      )}
      <div>
        <p className="text-xs font-semibold text-[#8A97A5] uppercase tracking-wider">{title}</p>
        <div className="flex items-baseline gap-1 mt-0.5">
          <span className="text-2xl font-bold text-[#1C2733]">{value}</span>
          <span className="text-xs font-semibold text-[#8A97A5]">{unit}</span>
        </div>
      </div>
    </Card>
  );
};

export default HealthMetricCard;
