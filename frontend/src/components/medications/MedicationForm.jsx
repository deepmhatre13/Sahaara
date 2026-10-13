import React, { useState } from 'react';
import Input from '../common/Input';
import Button from '../common/Button';
import { Pill, Clock } from 'lucide-react';

export const MedicationForm = ({ onSubmit, isLoading }) => {
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('');
  const [time, setTime] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim() || !dosage.trim()) return;
    onSubmit?.({ name: name.trim(), dosage: dosage.trim(), scheduled_time: time });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input label="Medication Name" icon={Pill} value={name} onChange={(e) => setName(e.target.value)} required />
      <Input label="Dosage" placeholder="e.g. 500mg, 1 tablet" value={dosage} onChange={(e) => setDosage(e.target.value)} required />
      <Input label="Scheduled Time" type="time" icon={Clock} value={time} onChange={(e) => setTime(e.target.value)} required />
      <Button type="submit" variant="primary" fullWidth isLoading={isLoading}>
        Add Medication
      </Button>
    </form>
  );
};

export default MedicationForm;
