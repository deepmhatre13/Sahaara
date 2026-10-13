import React from 'react';

export const Card = ({ children, className = '', title, subtitle, action, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-2xl p-6 border border-[#DDE3E8] shadow-xs ${onClick ? 'cursor-pointer hover:border-[#1E3A5F] transition-colors' : ''} ${className}`}
    >
      {(title || action) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && <h3 className="font-bold text-lg text-[#1C2733]">{title}</h3>}
            {subtitle && <p className="text-xs text-[#8A97A5] mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
