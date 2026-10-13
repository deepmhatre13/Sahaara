import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const HealthStatsChart = ({ data = [], metricType = 'heart_rate', unit = '' }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-[#DDE3E8] text-center text-sm text-[#8A97A5]">
        No trend data available for this metric
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-2xl border border-[#DDE3E8]">
      <h3 className="text-base font-bold text-[#1C2733] mb-4 uppercase tracking-wider text-xs">Telemetry Trend</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1E3A5F" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#1E3A5F" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F4F1EC" />
            <XAxis dataKey="timestamp" stroke="#8A97A5" fontSize={12} />
            <YAxis stroke="#8A97A5" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#FFFFFF',
                borderRadius: '12px',
                border: '1px solid #DDE3E8',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              }}
              formatter={(val) => [`${val} ${unit}`, 'Value']}
            />
            <Area type="monotone" dataKey="value" stroke="#1E3A5F" strokeWidth={2.5} fillOpacity={1} fill="url(#colorValue)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default HealthStatsChart;
