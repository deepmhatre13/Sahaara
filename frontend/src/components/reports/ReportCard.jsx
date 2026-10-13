import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { FileText, Calendar, CheckCircle2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const ReportCard = ({ report, onSelect }) => {
  return (
    <Card hover onClick={() => onSelect(report)} className="flex items-start justify-between gap-4">
      <div className="flex items-start gap-3.5">
        <div className="p-3 bg-[#1E3A5F]/10 text-[#1E3A5F] rounded-xl shrink-0 mt-0.5">
          <FileText size={22} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-base font-bold text-[#1C2733]">{report.filename || report.title || 'Medical Lab Report'}</h4>
            <Badge variant="success">Analyzed</Badge>
          </div>
          <p className="text-xs text-[#8A97A5] mt-1 flex items-center gap-1">
            <Calendar size={13} />
            <span>{report.uploaded_at ? formatDistanceToNow(new Date(report.uploaded_at), { addSuffix: true }) : 'Recently'}</span>
          </p>
          {report.summary && <p className="text-xs text-[#1C2733]/80 mt-2 line-clamp-2">{report.summary}</p>}
        </div>
      </div>
    </Card>
  );
};

export default ReportCard;

