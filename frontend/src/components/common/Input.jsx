import React from 'react';

export const Input = ({
  label,
  type = 'text',
  placeholder = '',
  icon: Icon,
  error,
  value,
  onChange,
  className = '',
  disabled = false,
  required = false,
  ...props
}) => {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label className="text-xs font-bold text-[#1C2733] uppercase tracking-wider">
          {label} {required && <span className="text-[#C0392B]">*</span>}
        </label>
      )}
      <div className="relative flex items-center">
        {Icon && (
          <div className="absolute left-3.5 text-[#8A97A5] pointer-events-none">
            <Icon size={18} />
          </div>
        )}
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={`w-full bg-[#F4F1EC]/50 border ${
            error ? 'border-[#C0392B]' : 'border-[#DDE3E8]'
          } rounded-xl ${
            Icon ? 'pl-10' : 'pl-4'
          } pr-4 py-2.5 text-sm text-[#1C2733] placeholder-[#8A97A5] focus:outline-hidden focus:border-[#1E3A5F] focus:bg-white transition-all disabled:opacity-50`}
          {...props}
        />
      </div>
      {error && <p className="text-xs font-semibold text-[#C0392B] mt-0.5">{error}</p>}
    </div>
  );
};

export default Input;
