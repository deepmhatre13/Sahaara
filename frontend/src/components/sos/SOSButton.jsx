import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export const SOSButton = ({ onConfirm, isLoading = false }) => {
  const [isHolding, setIsHolding] = useState(false);
  const [progress, setProgress] = useState(0);
  const [triggered, setTriggered] = useState(false);
  const timerRef = useRef(null);
  const startTimeRef = useRef(null);

  const HOLD_DURATION = 3000; // 3 seconds hold to confirm

  const startHold = () => {
    if (triggered || isLoading) return;
    setIsHolding(true);
    startTimeRef.current = Date.now();

    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      const pct = Math.min(100, (elapsed / HOLD_DURATION) * 100);
      setProgress(pct);

      if (pct >= 100) {
        clearInterval(timerRef.current);
        setTriggered(true);
        setIsHolding(false);
        if (onConfirm) onConfirm();
      }
    }, 30);
  };

  const cancelHold = () => {
    if (triggered) return;
    if (timerRef.current) clearInterval(timerRef.current);
    setIsHolding(false);
    setProgress(0);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // SVG parameters for circular progress ring
  const size = 200;
  const strokeWidth = 10;
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div
        className="relative flex items-center justify-center select-none touch-none"
        onMouseDown={startHold}
        onMouseUp={cancelHold}
        onMouseLeave={cancelHold}
        onTouchStart={startHold}
        onTouchEnd={cancelHold}
      >
        {/* SVG Circular Ring for progress */}
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke="#DDE3E8"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke="#C0392B"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-75"
          />
        </svg>

        {/* SOS Button Core with continuous pulse */}
        <motion.button
          animate={!isHolding && !triggered ? { scale: [1, 1.03, 1] } : { scale: isHolding ? 0.95 : 1 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          disabled={isLoading || triggered}
          className={`absolute w-36 h-36 rounded-full shadow-2xl flex flex-col items-center justify-center text-white font-extrabold focus:outline-none cursor-pointer transition-colors ${
            triggered ? 'bg-[#2E8B57]' : 'bg-[#C0392B] hover:bg-[#a83225]'
          }`}
        >
          {triggered ? (
            <>
              <CheckCircle2 size={44} className="mb-1" />
              <span className="text-base uppercase tracking-wider">SENT</span>
            </>
          ) : (
            <>
              <AlertTriangle size={44} className="mb-1 animate-pulse" />
              <span className="text-2xl uppercase tracking-widest">SOS</span>
            </>
          )}
        </motion.button>
      </div>

      {/* Reassuring text instructions */}
      <div className="text-center mt-6">
        <p className="text-lg font-bold text-[#1C2733]">
          {isHolding ? 'HOLDING... KEEP PRESSING' : triggered ? 'Help is on the way!' : 'Press & Hold for 3 Seconds'}
        </p>
        <p className="text-sm font-medium text-[#8A97A5] mt-1 max-w-xs">
          {triggered
            ? 'Your emergency contacts and response center have been notified.'
            : 'Designed to prevent accidental triggers while ensuring rapid emergency response.'}
        </p>
      </div>
    </div>
  );
};

export default SOSButton;

