import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import { UploadCloud, FileText } from 'lucide-react';

export const ReportUpload = ({ onUpload, isLoading }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    onUpload(selectedFile);
    setSelectedFile(null);
  };

  return (
    <Card className="p-6 border-dashed border-2 border-[#5B8CB8]/40 bg-[#F4F1EC]/30">
      <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center text-center">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleFileDrop}
          className={`w-full py-8 px-4 rounded-xl transition-colors cursor-pointer flex flex-col items-center ${
            dragOver ? 'bg-[#5B8CB8]/10' : ''
          }`}
        >
          <div className="w-16 h-16 rounded-2xl bg-[#1E3A5F]/10 text-[#1E3A5F] flex items-center justify-center mb-3">
            <UploadCloud size={32} />
          </div>

          <h4 className="text-base font-bold text-[#1C2733] mb-1">
            {selectedFile ? selectedFile.name : 'Drag and drop your report file here'}
          </h4>
          <p className="text-xs text-[#8A97A5] mb-4">Accepts images (PNG, JPG) or PDF medical lab reports</p>

          <label className="cursor-pointer">
            <input type="file" accept="image/*,.pdf" onChange={handleFileSelect} className="hidden" />
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-[#DDE3E8] rounded-xl text-sm font-semibold text-[#1C2733] hover:bg-[#F4F1EC]">
              <FileText size={16} />
              <span>Browse Files</span>
            </span>
          </label>
        </div>

        {selectedFile && (
          <div className="mt-4 w-full flex justify-end">
            <Button type="submit" variant="primary" isLoading={isLoading}>
              Upload & Analyze Report
            </Button>
          </div>
        )}
      </form>
    </Card>
  );
};

export default ReportUpload;

