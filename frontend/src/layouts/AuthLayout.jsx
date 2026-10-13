import React from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-[#F4F1EC] flex flex-col justify-center items-center p-4 sm:p-6">
      <div className="w-full max-w-md">
        {/* Logo / Lockup Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#1E3A5F] text-white shadow-lg mb-3">
            <span className="font-bold text-2xl tracking-tight">S</span>
          </div>
          <h1 className="text-3xl font-bold text-[#1C2733] tracking-tight">Sahaara</h1>
          <p className="text-sm font-medium text-[#8A97A5] mt-1">
            सहारा <span className="mx-1">•</span> Intelligent Elder Care
          </p>
        </div>

        {/* Animated Container Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 border border-[#DDE3E8]"
        >
          <Outlet />
        </motion.div>

        {/* Footer info */}
        <p className="text-center text-xs text-[#8A97A5] mt-8">
          &copy; {new Date().getFullYear()} Sahaara Care Platform. Safe, warm & reliable.
        </p>
      </div>
    </div>
  );
};

export default AuthLayout;
