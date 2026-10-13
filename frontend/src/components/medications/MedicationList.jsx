import React from 'react';
import MedicationCard from './MedicationCard';
import EmptyState from '../common/EmptyState';
import { Pill } from 'lucide-react';

export const MedicationList = ({ medications = [], onDelete }) => {
  if (!medications || medications.length === 0) {
    return <EmptyState icon={Pill} title="No Medications" description="No scheduled medications found." />;
  }

  return (
    <div className="space-y-3">
      {medications.map((m) => (
        <MedicationCard key={m.id} medication={m} onDelete={onDelete} />
      ))}
    </div>
  );
};

export default MedicationList;
