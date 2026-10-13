import React, { useState } from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';
import Modal from '../common/Modal';
import { User, Phone, Mail, ShieldCheck, Trash2 } from 'lucide-react';

export const CaregiverCard = ({ caregiver, onDelete }) => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(caregiver.id);
      setIsConfirmOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card hover className="flex flex-col justify-between h-full">
        <div>
          <div className="flex items-start justify-between gap-2 mb-3">
            <div className="p-3 bg-[#1E3A5F]/10 text-[#1E3A5F] rounded-xl">
              <User size={24} />
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={caregiver.is_primary ? 'success' : 'info'}>
                {caregiver.is_primary ? 'Primary Contact' : 'Caregiver'}
              </Badge>
              {onDelete && (
                <button
                  onClick={() => setIsConfirmOpen(true)}
                  className="p-1 text-[#8A97A5] hover:text-[#C0392B] rounded-lg transition-colors cursor-pointer"
                  title="Remove Caregiver"
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          </div>

          <h4 className="text-lg font-bold text-[#1C2733]">{caregiver.name || caregiver.full_name}</h4>
          <p className="text-xs font-semibold text-[#8A97A5] capitalize mt-0.5">{caregiver.relationship || 'Emergency Contact'}</p>

          <div className="mt-4 pt-3 border-t border-[#DDE3E8] space-y-2 text-xs">
            {caregiver.phone && (
              <div className="flex items-center gap-2 text-[#1C2733] font-semibold">
                <Phone size={14} className="text-[#2E8B57]" />
                <span>{caregiver.phone}</span>
              </div>
            )}
            {caregiver.email && (
              <div className="flex items-center gap-2 text-[#8A97A5]">
                <Mail size={14} />
                <span>{caregiver.email}</span>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Remove Confirmation Modal */}
      {onDelete && (
        <Modal isOpen={isConfirmOpen} onClose={() => setIsConfirmOpen(false)} title="Remove Caregiver Contact">
          <p className="text-sm text-[#8A97A5] mb-6">
            Are you sure you want to remove <strong className="text-[#1C2733]">{caregiver.name || caregiver.full_name}</strong> from your emergency response contacts?
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setIsConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete} isLoading={loading}>
              Remove Contact
            </Button>
          </div>
        </Modal>
      )}
    </>
  );
};

export default CaregiverCard;

