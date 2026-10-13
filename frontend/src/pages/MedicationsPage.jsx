import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { getMedications, createMedication, deleteMedication } from '../api/medications';
import MedicationList from '../components/medications/MedicationList';
import MedicationForm from '../components/medications/MedicationForm';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export const MedicationsPage = () => {
  const { user } = useAuth();
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchMedications = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getMedications(user.id);
      setMedications(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchMedications();
  }, [fetchMedications]);

  const handleCreate = async (payload) => {
    if (!user?.id) return;
    setSubmitting(true);
    try {
      await createMedication({ ...payload, user_id: user.id });
      toast.success('Medication added to your schedule');
      setIsModalOpen(false);
      fetchMedications();
    } catch (err) {
      console.error(err);
      toast.error('Failed to add medication');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteMedication(id);
      toast.success('Medication deleted');
      fetchMedications();
    } catch (err) {
      console.error(err);
      toast.error('Failed to delete medication');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#DDE3E8]">
        <div>
          <h2 className="text-2xl font-bold text-[#1C2733]">Medication Schedule</h2>
          <p className="text-sm text-[#8A97A5] mt-0.5">Track and manage your daily prescription dosages</p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <Plus size={18} />
          <span>Add Medication</span>
        </Button>
      </div>

      {/* Medication Cards List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <MedicationList medications={medications} onDelete={handleDelete} />
      )}

      {/* Add Medication Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Medication">
        <MedicationForm onSubmit={handleCreate} isLoading={submitting} />
      </Modal>
    </div>
  );
};

export default MedicationsPage;
