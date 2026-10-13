import React, { useState } from 'react';
import Button from '../common/Button';
import { RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import useAuth from '../../hooks/useAuth';
import { syncHealthData } from '../../api/healthData';

export const SyncHealthDataButton = ({ onSyncSuccess }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleSync = async () => {
    if (!user?.id || loading) return;
    try {
      setLoading(true);
      await syncHealthData(user.id);
      toast.success('Health data synced successfully!');
      onSyncSuccess?.();
    } catch (err) {
      toast.error('Failed to sync health telemetry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      variant="secondary"
      size="sm"
      isLoading={loading}
      onClick={handleSync}
      className="gap-2"
    >
      <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
      <span>Sync Telemetry</span>
    </Button>
  );
};

export default SyncHealthDataButton;
