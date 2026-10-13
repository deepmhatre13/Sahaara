import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { getHealthSummary, getHealthMetrics } from '../api/healthData';
import HealthMetricCard from '../components/health/HealthMetricCard';
import HealthStatsChart from '../components/health/HealthStatsChart';
import SyncHealthDataButton from '../components/health/SyncHealthDataButton';
import { METRIC_TYPES } from '../utils/constants';
import { Heart, Activity, Moon, Footprints } from 'lucide-react';
import Spinner from '../components/common/Spinner';

export const HealthPage = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('heart_rate');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHealthData = useCallback(async () => {
    if (!user?.id) return;
    try {
      setLoading(true);
      const [sumRes, metricsRes] = await Promise.all([
        getHealthSummary(user.id),
        getHealthMetrics(user.id, selectedMetric),
      ]);
      setSummary(sumRes);
      
      // Transform metric response array for recharts
      const formatted = (metricsRes || []).map((m) => ({
        timestamp: new Date(m.timestamp || m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        value: m.value,
      }));
      setChartData(formatted);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id, selectedMetric]);

  useEffect(() => {
    fetchHealthData();
  }, [fetchHealthData]);

  const activeMetricObj = METRIC_TYPES.find((m) => m.id === selectedMetric) || METRIC_TYPES[0];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Bar Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#DDE3E8]">
        <div>
          <h2 className="text-2xl font-bold text-[#1C2733]">Vitals & Health Snapshot</h2>
          <p className="text-sm text-[#8A97A5] mt-0.5">Real-time health telemetry and historical analytics</p>
        </div>
        <SyncHealthDataButton onSyncSuccess={fetchHealthData} />
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <HealthMetricCard title="Heart Rate" value={summary?.heart_rate || 72} unit="BPM" icon={Heart} color="text-red-500" />
        <HealthMetricCard title="Blood Oxygen" value={summary?.spo2 || 98} unit="%" icon={Activity} color="text-blue-500" />
        <HealthMetricCard title="Sleep Quality" value={summary?.sleep_hours || 7.5} unit="hrs" icon={Moon} color="text-indigo-500" />
        <HealthMetricCard title="Daily Steps" value={summary?.steps ? summary.steps.toLocaleString() : '4,250'} unit="steps" icon={Footprints} color="text-emerald-500" />
      </div>

      {/* Metric Type Selector Tabs */}
      <div className="flex flex-wrap gap-2">
        {METRIC_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedMetric(type.id)}
            className={`px-4 py-2.5 rounded-xl font-semibold text-sm transition-colors cursor-pointer ${
              selectedMetric === type.id
                ? 'bg-[#1E3A5F] text-white shadow-xs'
                : 'bg-white text-[#1C2733] border border-[#DDE3E8] hover:bg-[#F4F1EC]'
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* Recharts Component */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <HealthStatsChart data={chartData} metricType={selectedMetric} unit={activeMetricObj.unit} />
      )}
    </div>
  );
};

export default HealthPage;
