import React from 'react';

export const Badge = ({ children, variant = 'neutral', size = 'md', className = '' }) => {
  const variants = {
    neutral: 'bg-[#F4F1EC] text-[#1C2733] border border-[#DDE3E8]',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border border-rose-200',
    info: 'bg-sky-50 text-sky-700 border border-sky-200',
    primary: 'bg-[#1E3A5F]/10 text-[#1E3A5F] border border-[#1E3A5F]/20',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };

  return (
    <span
      className={`inline-flex items-center font-bold rounded-full ${variants[variant] || variants.neutral} ${
        sizes[size] || sizes.md
      } ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
