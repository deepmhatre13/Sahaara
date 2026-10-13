import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import usePolling from '../hooks/usePolling';
import { startMonitoring, getActivityStatus, getActivityEvents } from '../api/activity';
import ActivityStatusIndicator from '../components/activity/ActivityStatusIndicator';
import ActivityTimeline from '../components/activity/ActivityTimeline';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';

export const ActivityPage = () => {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!user?.id) return;
    try {
      const [statusRes, eventsRes] = await Promise.all([
        getActivityStatus(user.id),
        getActivityEvents(user.id),
      ]);
      setStatus(statusRes);
      setEvents(eventsRes || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    const initMonitoring = async () => {
      if (user?.id) {
        try {
          await startMonitoring(user.id);
        } catch (e) {
          // ignore if already started
        }
        fetchData();
      }
    };
    initMonitoring();
  }, [user?.id, fetchData]);

  // Poll status every 8 seconds
  usePolling(fetchData, 8000, !!user?.id);

  if (loading && !status) {
    return (
      <div className="flex justify-center items-center py-16">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Banner with Large Indicator */}
      <Card className="p-8 text-center bg-white border-t-4 border-t-[#1E3A5F]">
        <h2 className="text-2xl font-bold text-[#1C2733] mb-4">Elder Activity & Motion Monitor</h2>
        <div className="flex justify-center mb-4">
          <ActivityStatusIndicator status={status?.current_status || 'MOTION_DETECTED'} />
        </div>
        <p className="text-sm font-semibold text-[#8A97A5]">
          Continuous non-intrusive ambient sensor monitoring active.
        </p>
      </Card>

      {/* Activity Timeline */}
      <ActivityTimeline events={events} />
    </div>
  );
};

export default ActivityPage;
