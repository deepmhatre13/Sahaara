import React from 'react';
import Card from '../common/Card';

export const ReportExplanationView = ({ explanation }) => {
  if (!explanation) return null;

  return (
    <Card className="p-6 bg-white border-l-4 border-l-[#D98E4A]">
      <h4 className="text-lg font-bold text-[#1C2733] mb-3">AI Lab Report Summary & Insights</h4>
      <div className="text-sm text-[#1C2733]/90 space-y-2 whitespace-pre-line leading-relaxed">
        {explanation}
      </div>
    </Card>
  );
};

export default ReportExplanationView;

