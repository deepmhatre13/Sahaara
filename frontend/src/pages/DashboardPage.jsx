import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import usePolling from '../hooks/usePolling';
import { getDashboardData } from '../api/dashboard';
import DashboardSummaryCards from '../components/dashboard/DashboardSummaryCards';
import ActivityStatusCard from '../components/dashboard/ActivityStatusCard';
import HealthSnapshotCard from '../components/dashboard/HealthSnapshotCard';
import UpcomingRemindersCard from '../components/dashboard/UpcomingRemindersCard';
import RecentNotificationsCard from '../components/dashboard/RecentNotificationsCard';
import Spinner from '../components/common/Spinner';

export const DashboardPage = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getDashboardData(user.id);
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  // Poll dashboard every 30 seconds
  usePolling(fetchDashboard, 30000, !!user?.id);

  const currentDateStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

  if (loading && !dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Spinner size="lg" />
        <p className="text-sm font-semibold text-[#8A97A5] mt-4">Loading your care dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Greeting Header */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#DDE3E8]">
        <h2 className="text-2xl sm:text-3xl font-bold text-[#1C2733]">
          Good day, {user?.full_name || 'Care Seeker'}
        </h2>
        <p className="text-sm font-semibold text-[#8A97A5] mt-1">{currentDateStr}</p>
      </div>

      {/* Grid of Top Summary Cards */}
      <DashboardSummaryCards data={dashboardData} />

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ActivityStatusCard statusData={dashboardData?.activity_status} />
        <HealthSnapshotCard summary={dashboardData?.health_summary} onSyncSuccess={fetchDashboard} />
        <UpcomingRemindersCard
          medications={dashboardData?.upcoming_medications}
          appointments={dashboardData?.upcoming_appointments}
        />
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RecentNotificationsCard notifications={dashboardData?.recent_notifications} />
      </div>
    </div>
  );
};

export default DashboardPage;
