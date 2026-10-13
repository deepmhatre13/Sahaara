import React, { useState } from 'react';
import Input from '../common/Input';
import Button from '../common/Button';

export const AppointmentForm = ({ onSubmit, isLoading }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() || !scheduledAt) return;
    onSubmit({
      title,
      description,
      location,
      scheduled_at: scheduledAt,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Appointment Title"
        placeholder="e.g. Cardiologist Checkup"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <Input
        label="Date & Time"
        type="datetime-local"
        value={scheduledAt}
        onChange={(e) => setScheduledAt(e.target.value)}
        required
      />

      <Input
        label="Location / Clinic"
        placeholder="e.g. City Care Hospital, Room 302"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />

      <Input
        label="Description / Purpose"
        placeholder="e.g. Routine blood test and BP measurement"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <div className="pt-2 flex justify-end">
        <Button type="submit" variant="primary" isLoading={isLoading} fullWidth>
          Schedule Appointment
        </Button>
      </div>
    </form>
  );
};

export default AppointmentForm;

