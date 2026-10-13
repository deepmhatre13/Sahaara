import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { triggerSos, getSosHistory, resolveSosEvent } from '../api/sos';
import SOSButton from '../components/sos/SOSButton';
import EmergencyHistoryList from '../components/sos/EmergencyHistoryList';
import Card from '../components/common/Card';
import toast from 'react-hot-toast';
import Spinner from '../components/common/Spinner';

export const SOSPage = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  const fetchHistory = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getSosHistory(user.id);
      setHistory(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleSosTrigger = async () => {
    if (!user?.id) return;
    setTriggering(true);
    try {
      await triggerSos({
        user_id: user.id,
        source: 'sos_button',
        message: 'Manual Emergency SOS triggered by elder user.',
      });
      toast.success('Emergency SOS Alert Sent!');
      fetchHistory();
    } catch (err) {
      console.error(err);
      toast.error('Failed to dispatch SOS alert. Please retry!');
    } finally {
      setTriggering(false);
    }
  };

  const handleResolve = async (eventId, note) => {
    try {
      await resolveSosEvent(eventId, note);
      toast.success('Event marked as resolved');
      fetchHistory();
    } catch (err) {
      console.error(err);
      toast.error('Failed to resolve event');
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* SOS Button Hero Section */}
      <Card className="p-8 border-t-8 border-t-[#C0392B] bg-white text-center">
        <h2 className="text-2xl font-bold text-[#1C2733] mb-2">Emergency Response Station</h2>
        <p className="text-sm text-[#8A97A5] max-w-md mx-auto mb-6">
          Pressing and holding the SOS button for 3 seconds will instantly notify your caregivers and Sahaara emergency response team.
        </p>

        <SOSButton onConfirm={handleSosTrigger} isLoading={triggering} />
      </Card>

      {/* Emergency History Section */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-[#1C2733]">Emergency Signal Log</h3>
        {loading ? (
          <div className="flex justify-center py-8">
            <Spinner size="md" />
          </div>
        ) : (
          <EmergencyHistoryList events={history} onResolve={handleResolve} />
        )}
      </div>
    </div>
  );
};

export default SOSPage;
