import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export const Modal = ({ isOpen, onClose, title, children, maxWidth = 'max-w-lg' }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div
        className={`bg-white rounded-2xl w-full ${maxWidth} border border-[#DDE3E8] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150`}
        role="dialog"
      >
        <div className="flex items-center justify-between p-6 border-b border-[#DDE3E8]">
          <h3 className="font-bold text-lg text-[#1C2733]">{title}</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#8A97A5] hover:text-[#1C2733] hover:bg-[#F4F1EC] transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
