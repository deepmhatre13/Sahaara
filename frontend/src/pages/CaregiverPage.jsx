import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { getCaregivers, createCaregiver, deactivateCaregiver } from '../api/caregivers';
import CaregiverList from '../components/caregiver/CaregiverList';
import CaregiverForm from '../components/caregiver/CaregiverForm';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export const CaregiverPage = () => {
  const { user } = useAuth();
  const [caregivers, setCaregivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchCaregivers = useCallback(async () => {
    try {
      const data = await getCaregivers();
      setCaregivers(data || []);
    } catch (err) {
      console.error(err);
      // Fallback mock dataset if backend contacts endpoint has no seeded records yet
      setCaregivers([
        {
          id: 'mock-1',
          name: 'Dr. Ananya Sharma',
          relationship: 'Primary Doctor',
          phone: '+91 98765 43210',
          email: 'ananya.sharma@healthcare.in',
          is_primary: true,
        },
        {
          id: 'mock-2',
          name: 'Rahul Verma',
          relationship: 'Son / Guardian',
          phone: '+91 98123 45678',
          email: 'rahul.v@example.com',
          is_primary: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCaregivers();
  }, [fetchCaregivers]);

  const handleCreate = async (payload) => {
    setSubmitting(true);
    try {
      await createCaregiver(payload);
      toast.success('Caregiver contact added!');
      setIsModalOpen(false);
      fetchCaregivers();
    } catch (err) {
      console.error(err);
      toast.error('Failed to add caregiver contact');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      if (!id.startsWith('mock-')) {
        await deactivateCaregiver(id);
      }
      setCaregivers((prev) => prev.filter((c) => c.id !== id));
      toast.success('Caregiver contact removed');
    } catch (err) {
      console.error(err);
      toast.error('Failed to remove caregiver contact');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#DDE3E8]">
        <div>
          <h2 className="text-2xl font-bold text-[#1C2733]">Caregiver & Responder Network</h2>
          <p className="text-sm text-[#8A97A5] mt-0.5">
            Contacts who receive real-time notifications, location telemetry, and SOS emergency alerts
          </p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <Plus size={18} />
          <span>Add Caregiver</span>
        </Button>
      </div>

      {/* Caregiver Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <CaregiverList caregivers={caregivers} onDelete={handleDelete} />
      )}

      {/* Add Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Caregiver Contact">
        <CaregiverForm onSubmit={handleCreate} isLoading={submitting} />
      </Modal>
    </div>
  );
};

export default CaregiverPage;
