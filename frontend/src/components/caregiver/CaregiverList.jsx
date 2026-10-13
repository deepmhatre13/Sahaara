import React from 'react';
import CaregiverCard from './CaregiverCard';
import EmptyState from '../common/EmptyState';
import { Users } from 'lucide-react';

export const CaregiverList = ({ caregivers = [], onDelete }) => {
  if (caregivers.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="No Caregivers Assigned"
        description="Add family members, nurses, or emergency contacts to be notified during SOS signals."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {caregivers.map((cg) => (
        <CaregiverCard key={cg.id} caregiver={cg} onDelete={onDelete} />
      ))}
    </div>
  );
};

export default CaregiverList;

