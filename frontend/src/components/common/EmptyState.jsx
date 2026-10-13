import React from 'react';

export const EmptyState = ({ icon: Icon, title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white rounded-2xl border border-[#DDE3E8]">
      {Icon && (
        <div className="p-4 bg-[#F4F1EC] text-[#1E3A5F] rounded-2xl mb-4">
          <Icon size={32} />
        </div>
      )}
      {title && <h3 className="font-bold text-lg text-[#1C2733]">{title}</h3>}
      {description && <p className="text-sm text-[#8A97A5] max-w-sm mt-1">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};

export default EmptyState;
