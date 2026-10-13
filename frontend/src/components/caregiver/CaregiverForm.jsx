import React, { useState } from 'react';
import Input from '../common/Input';
import Button from '../common/Button';

export const CaregiverForm = ({ onSubmit, isLoading }) => {
  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('Son / Daughter');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [isPrimary, setIsPrimary] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim()) return;
    onSubmit({
      name,
      relationship,
      phone,
      email,
      is_primary: isPrimary,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Full Name"
        placeholder="e.g. Dr. Priya Sharma / Rajesh Verma"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-semibold text-[#1C2733]">Relationship</label>
        <select
          value={relationship}
          onChange={(e) => setRelationship(e.target.value)}
          className="w-full bg-white border border-[#DDE3E8] text-[#1C2733] text-base rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]"
        >
          <option value="Son / Daughter">Son / Daughter</option>
          <option value="Spouse">Spouse</option>
          <option value="Family Nurse">Family Nurse</option>
          <option value="Primary Doctor">Primary Doctor</option>
          <option value="Neighbor">Neighbor</option>
        </select>
      </div>

      <Input
        label="Phone Number (for SMS & SOS Alerts)"
        type="tel"
        placeholder="+91 98765 43210"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        required
      />

      <Input
        label="Email Address"
        type="email"
        placeholder="caregiver@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <div className="flex items-center gap-2 pt-2">
        <input
          id="isPrimary"
          type="checkbox"
          checked={isPrimary}
          onChange={(e) => setIsPrimary(e.target.checked)}
          className="w-4 h-4 text-[#1E3A5F] rounded focus:ring-[#1E3A5F]"
        />
        <label htmlFor="isPrimary" className="text-sm font-semibold text-[#1C2733] cursor-pointer">
          Designate as Primary Emergency Responder
        </label>
      </div>

      <div className="pt-2 flex justify-end">
        <Button type="submit" variant="primary" isLoading={isLoading} fullWidth>
          Add Caregiver
        </Button>
      </div>
    </form>
  );
};

export default CaregiverForm;

