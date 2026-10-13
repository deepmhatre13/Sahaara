import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { getAppointments, createAppointment, deleteAppointment } from '../api/appointments';
import AppointmentList from '../components/appointments/AppointmentList';
import AppointmentForm from '../components/appointments/AppointmentForm';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export const AppointmentsPage = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchAppointments = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getAppointments(user.id);
      setAppointments(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  const handleCreate = async (payload) => {
    if (!user?.id) return;
    setSubmitting(true);
    try {
      await createAppointment({ ...payload, user_id: user.id });
      toast.success('Appointment scheduled');
      setIsModalOpen(false);
      fetchAppointments();
    } catch (err) {
      console.error(err);
      toast.error('Failed to schedule appointment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteAppointment(id);
      toast.success('Appointment removed');
      fetchAppointments();
    } catch (err) {
      console.error(err);
      toast.error('Failed to delete appointment');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#DDE3E8]">
        <div>
          <h2 className="text-2xl font-bold text-[#1C2733]">Upcoming Appointments</h2>
          <p className="text-sm text-[#8A97A5] mt-0.5">Manage doctor visits, health checks and caregiver consultations</p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <Plus size={18} />
          <span>New Appointment</span>
        </Button>
      </div>

      {/* Appointments Grid List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <AppointmentList appointments={appointments} onDelete={handleDelete} />
      )}

      {/* Add Appointment Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Schedule New Appointment">
        <AppointmentForm onSubmit={handleCreate} isLoading={submitting} />
      </Modal>
    </div>
  );
};

export default AppointmentsPage;
