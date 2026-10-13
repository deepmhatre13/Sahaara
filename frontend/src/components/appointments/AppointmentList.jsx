import React from 'react';
import AppointmentCard from './AppointmentCard';
import EmptyState from '../common/EmptyState';
import { Calendar } from 'lucide-react';

export const AppointmentList = ({ appointments = [], onDelete }) => {
  if (appointments.length === 0) {
    return (
      <EmptyState
        icon={Calendar}
        title="No Upcoming Appointments"
        description="You have no scheduled medical or care appointments."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {appointments.map((app) => (
        <AppointmentCard key={app.id} appointment={app} onDelete={onDelete} />
      ))}
    </div>
  );
};

export default AppointmentList;

