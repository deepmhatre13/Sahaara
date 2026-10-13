import React from 'react';

export const ChatSourcesFooter = ({ sources = [] }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2.5 pt-2 border-t border-[#DDE3E8]/60 text-xs">
      <span className="font-semibold text-[#8A97A5] block mb-1">Referenced Sources:</span>
      <div className="flex flex-wrap gap-1.5">
        {sources.map((src, idx) => (
          <span
            key={idx}
            className="bg-[#F4F1EC] text-[#1E3A5F] px-2 py-0.5 rounded-md font-medium text-[11px] border border-[#DDE3E8]"
          >
            {typeof src === 'string' ? src : src.title || src.name || `Source ${idx + 1}`}
          </span>
        ))}
      </div>
    </div>
  );
};

export default ChatSourcesFooter;

