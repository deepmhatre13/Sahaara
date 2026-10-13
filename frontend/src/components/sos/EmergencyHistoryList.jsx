import React from 'react';
import EmergencyEventCard from './EmergencyEventCard';
import EmptyState from '../common/EmptyState';
import { ShieldAlert } from 'lucide-react';

export const EmergencyHistoryList = ({ events = [], onResolve }) => {
  if (events.length === 0) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="No Emergency History"
        description="There are no past emergency SOS events logged for your account."
      />
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <EmergencyEventCard key={event.id} event={event} onResolve={onResolve} />
      ))}
    </div>
  );
};

export default EmergencyHistoryList;

