import React, { useState, useEffect, useCallback } from 'react';
import useAuth from '../hooks/useAuth';
import { uploadReport, getReports } from '../api/reports';
import ReportUpload from '../components/reports/ReportUpload';
import ReportCard from '../components/reports/ReportCard';
import ReportExplanationView from '../components/reports/ReportExplanationView';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import { FileText } from 'lucide-react';
import toast from 'react-hot-toast';

export const ReportsPage = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fetchReports = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getReports(user.id);
      setReports(data || []);
      if (data && data.length > 0 && !selectedReport) {
        setSelectedReport(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.id, selectedReport]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleUpload = async (file) => {
    if (!user?.id) return;
    setUploading(true);
    try {
      const result = await uploadReport(user.id, file);
      toast.success('Medical report uploaded and analyzed!');
      setSelectedReport(result);
      fetchReports();
    } catch (err) {
      console.error(err);
      toast.error('Failed to upload report');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Upload Header */}
      <ReportUpload onUpload={handleUpload} isLoading={uploading} />

      {/* Selected Explanation View */}
      {selectedReport && (
        <ReportExplanationView explanation={selectedReport.explanation || selectedReport.summary} />
      )}

      {/* History Reports List */}
      <div className="space-y-4 pt-4">
        <h3 className="text-xl font-bold text-[#1C2733]">Past Medical Reports</h3>
        {loading ? (
          <div className="flex justify-center py-8">
            <Spinner size="md" />
          </div>
        ) : reports.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No Uploaded Reports"
            description="Upload blood tests, prescriptions, or doctor notes to generate instant AI health summaries."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reports.map((rep) => (
              <ReportCard key={rep.id} report={rep} onSelect={(r) => setSelectedReport(r)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
