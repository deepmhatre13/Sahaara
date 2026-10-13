import React, { useState } from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Modal from '../common/Modal';
import Button from '../common/Button';
import Input from '../common/Input';
import { AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const EmergencyEventCard = ({ event, onResolve }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const isResolved = event.status === 'RESOLVED';
  const isAck = event.status === 'ACKNOWLEDGED';

  const handleResolveSubmit = async () => {
    setLoading(true);
    try {
      await onResolve(event.id, note || 'Resolved by user/caregiver');
      setIsModalOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card className={`border-l-4 ${isResolved ? 'border-l-[#2E8B57]' : 'border-l-[#C0392B]'}`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`p-2.5 rounded-xl ${isResolved ? 'bg-[#2E8B57]/15 text-[#2E8B57]' : 'bg-[#C0392B]/15 text-[#C0392B]'}`}>
              {isResolved ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-bold text-[#1C2733] text-base sm:text-lg">
                  Emergency SOS Signal
                </h4>
                <Badge variant={isResolved ? 'success' : isAck ? 'warning' : 'danger'}>
                  {event.status}
                </Badge>
              </div>
              <p className="text-sm text-[#8A97A5] mt-0.5">{event.message || 'SOS Button Triggered'}</p>
              <div className="flex items-center gap-2 text-xs text-[#8A97A5] mt-2">
                <Clock size={14} />
                <span>
                  {event.created_at
                    ? formatDistanceToNow(new Date(event.created_at), { addSuffix: true })
                    : 'Recently'}
                </span>
                <span>• Source: {event.source || 'Mobile App'}</span>
              </div>
            </div>
          </div>

          {!isResolved && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(true)}
              className="border-[#C0392B] text-[#C0392B] hover:bg-[#C0392B]/10 self-start sm:self-center"
            >
              Mark Resolved
            </Button>
          )}
        </div>
      </Card>

      {/* Resolve Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Resolve Emergency Event">
        <div className="space-y-4">
          <p className="text-sm text-[#8A97A5]">
            Please enter a resolution note or confirmation before marking this event as safe and resolved.
          </p>
          <Input
            label="Resolution Note"
            placeholder="e.g. Caregiver verified elder is safe."
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleResolveSubmit} isLoading={loading}>
              Confirm Resolve
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default EmergencyEventCard;

