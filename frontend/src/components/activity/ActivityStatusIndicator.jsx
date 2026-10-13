import React from 'react';
import { motion } from 'framer-motion';

export const ActivityStatusIndicator = ({ status = 'MOTION_DETECTED' }) => {
  let label = 'Motion Detected';
  let dotColor = 'bg-[#2E8B57]';
  let pulseColor = 'bg-[#2E8B57]';
  let textColor = 'text-[#2E8B57]';
  let bgBadge = 'bg-[#2E8B57]/10 border-[#2E8B57]/30';

  if (status === 'NO_MOTION') {
    label = 'No Motion';
    dotColor = 'bg-[#E8A33D]';
    pulseColor = 'bg-[#E8A33D]';
    textColor = 'text-[#b57519]';
    bgBadge = 'bg-[#E8A33D]/10 border-[#E8A33D]/30';
  } else if (status === 'INACTIVITY_THRESHOLD_EXCEEDED') {
    label = 'Inactivity Alert';
    dotColor = 'bg-[#C0392B]';
    pulseColor = 'bg-[#C0392B]';
    textColor = 'text-[#C0392B]';
    bgBadge = 'bg-[#C0392B]/10 border-[#C0392B]/30';
  }

  return (
    <div className={`inline-flex items-center gap-2.5 px-3 py-1.5 rounded-full border ${bgBadge}`}>
      <div className="relative flex items-center justify-center">
        <motion.span
          animate={{ scale: [1, 1.8, 1], opacity: [0.7, 0, 0.7] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          className={`absolute w-3 h-3 rounded-full ${pulseColor}`}
        />
        <span className={`w-2.5 h-2.5 rounded-full ${dotColor} relative z-10`} />
      </div>
      <span className={`text-xs font-bold ${textColor}`}>{label}</span>
    </div>
  );
};

export default ActivityStatusIndicator;

