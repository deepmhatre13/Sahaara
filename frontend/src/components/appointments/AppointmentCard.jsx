import React, { useState } from 'react';
import Card from '../common/Card';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { Calendar, MapPin, Trash2, Clock } from 'lucide-react';
import { formatDistanceToNow, format, parseISO } from 'date-fns';

export const AppointmentCard = ({ appointment, onDelete }) => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(appointment.id);
      setIsConfirmOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const parsedDate = appointment.scheduled_at ? parseISO(appointment.scheduled_at) : new Date();

  return (
    <>
      <Card hover className="flex flex-col justify-between h-full">
        <div>
          <div className="flex items-start justify-between gap-2 mb-3">
            <div className="p-3 bg-[#1E3A5F]/10 text-[#1E3A5F] rounded-xl">
              <Calendar size={24} />
            </div>
            <button
              onClick={() => setIsConfirmOpen(true)}
              className="p-1.5 text-[#8A97A5] hover:text-[#C0392B] rounded-lg transition-colors cursor-pointer"
              title="Delete Appointment"
            >
              <Trash2 size={18} />
            </button>
          </div>

          <h4 className="text-lg font-bold text-[#1C2733]">{appointment.title}</h4>
          <p className="text-xs font-semibold text-[#8A97A5] mt-1 flex items-center gap-1">
            <Clock size={14} className="text-[#1E3A5F]" />
            <span>{formatDistanceToNow(parsedDate, { addSuffix: true })}</span>
          </p>

          <div className="mt-4 pt-3 border-t border-[#DDE3E8] space-y-2">
            <p className="text-sm font-bold text-[#1C2733]">
              {format(parsedDate, 'PPP p')}
            </p>
            {appointment.location && (
              <p className="text-xs text-[#8A97A5] flex items-center gap-1">
                <MapPin size={14} />
                <span>{appointment.location}</span>
              </p>
            )}
            {appointment.description && (
              <p className="text-xs text-[#8A97A5] italic line-clamp-2">{appointment.description}</p>
            )}
          </div>
        </div>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isConfirmOpen} onClose={() => setIsConfirmOpen(false)} title="Cancel Appointment">
        <p className="text-sm text-[#8A97A5] mb-6">
          Are you sure you want to cancel the appointment <strong className="text-[#1C2733]">{appointment.title}</strong>?
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setIsConfirmOpen(false)}>
            Keep Appointment
          </Button>
          <Button variant="danger" onClick={handleDelete} isLoading={loading}>
            Cancel Appointment
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default AppointmentCard;

