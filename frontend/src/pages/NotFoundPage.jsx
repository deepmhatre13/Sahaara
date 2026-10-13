import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import { Home, AlertCircle } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-20 h-20 bg-[#C0392B]/10 text-[#C0392B] rounded-3xl flex items-center justify-center mb-4">
        <AlertCircle size={40} />
      </div>
      <h2 className="text-3xl font-bold text-[#1C2733] mb-2">Page Not Found</h2>
      <p className="text-sm text-[#8A97A5] max-w-sm mb-6">
        The care module or page you were looking for does not exist or has been moved.
      </p>
      <Link to="/dashboard">
        <Button variant="primary" className="flex items-center gap-2">
          <Home size={18} />
          <span>Back to Dashboard</span>
        </Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;
