import React from 'react';
import Card from '../common/Card';
import { Pill, Calendar } from 'lucide-react';

export const UpcomingRemindersCard = ({ medications = [], appointments = [] }) => {
  const hasMeds = medications && medications.length > 0;
  const hasAppts = appointments && appointments.length > 0;

  return (
    <Card title="Upcoming Reminders">
      <div className="space-y-3 py-1">
        {!hasMeds && !hasAppts ? (
          <p className="text-sm text-[#8A97A5] text-center py-4">No upcoming reminders</p>
        ) : (
          <>
            {medications.slice(0, 2).map((m, idx) => (
              <div key={m.id || idx} className="p-3 bg-[#F4F1EC]/60 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Pill size={16} className="text-[#1E3A5F]" />
                  <div>
                    <p className="text-xs font-bold text-[#1C2733]">{m.name || m.medication_name}</p>
                    <p className="text-[10px] text-[#8A97A5]">{m.dosage}</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-[#1E3A5F]">{m.time}</span>
              </div>
            ))}

            {appointments.slice(0, 2).map((a, idx) => (
              <div key={a.id || idx} className="p-3 bg-[#F4F1EC]/60 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Calendar size={16} className="text-[#1E3A5F]" />
                  <div>
                    <p className="text-xs font-bold text-[#1C2733]">{a.doctor_name || a.title}</p>
                    <p className="text-[10px] text-[#8A97A5]">{a.specialty || 'Checkup'}</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-[#1E3A5F]">{a.time || a.date}</span>
              </div>
            ))}
          </>
        )}
      </div>
    </Card>
  );
};

export default UpcomingRemindersCard;
