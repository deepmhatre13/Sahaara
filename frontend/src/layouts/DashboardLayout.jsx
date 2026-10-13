import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import Topbar from '../components/layout/Topbar';
import { Menu, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

export const DashboardLayout = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Page title mapping based on route
  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/dashboard':
        return 'Dashboard Overview';
      case '/health':
        return 'Health Snapshot';
      case '/activity':
        return 'Activity Monitor';
      case '/sos':
        return 'Emergency SOS';
      case '/caregiver':
        return 'Caregiver Network';
      case '/chatbot':
        return 'AI Health Assistant';
      case '/reports':
        return 'Medical Reports';
      case '/medications':
        return 'Medications Schedule';
      case '/appointments':
        return 'Upcoming Appointments';
      case '/notifications':
        return 'Notification Center';
      default:
        return 'Sahaara Care';
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F1EC] flex flex-col md:flex-row">
      {/* Sidebar navigation */}
      <Sidebar isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Navbar Header */}
        <div className="md:hidden bg-white border-b border-[#DDE3E8] px-4 py-3 flex items-center justify-between sticky top-0 z-20">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-xl text-[#1C2733] hover:bg-[#F4F1EC]"
          >
            <Menu size={24} />
          </button>
          <div className="font-bold text-lg text-[#1E3A5F]">Sahaara</div>
          <div className="w-8" />
        </div>

        {/* Desktop Topbar */}
        <div className="hidden md:block">
          <Topbar title={getPageTitle(location.pathname)} />
        </div>

        {/* Outlet Content Container with fade animation */}
        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto pb-24 md:pb-8">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>

      {/* Persistent Floating SOS Quick-Access Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => navigate('/sos')}
        className="fixed bottom-6 right-6 z-40 bg-[#C0392B] text-white p-4 rounded-full shadow-2xl flex items-center justify-center gap-2 border-2 border-white hover:bg-[#a83225] transition-colors cursor-pointer"
        aria-label="Emergency SOS Quick Button"
      >
        <AlertTriangle size={26} className="animate-pulse" />
        <span className="font-extrabold text-sm uppercase tracking-wider pr-1">SOS</span>
      </motion.button>
    </div>
  );
};

export default DashboardLayout;
