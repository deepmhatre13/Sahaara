import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import Badge from '../common/Badge';
import { Pill, Trash2, Clock } from 'lucide-react';

export const MedicationCard = ({ medication, onDelete }) => {
  return (
    <Card className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="p-3 bg-[#1E3A5F]/10 text-[#1E3A5F] rounded-xl">
          <Pill size={22} />
        </div>
        <div>
          <h4 className="font-bold text-[#1C2733] text-base">{medication?.name}</h4>
          <p className="text-xs text-[#8A97A5] font-semibold mt-0.5">{medication?.dosage}</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#8A97A5]">
          <Clock size={14} />
          <span>{medication?.scheduled_time || medication?.time || 'Daily'}</span>
        </div>

        {onDelete && (
          <button
            onClick={() => onDelete(medication.id)}
            className="p-2 text-[#8A97A5] hover:text-[#C0392B] rounded-lg transition-colors cursor-pointer"
            title="Delete medication"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </Card>
  );
};

export default MedicationCard;
