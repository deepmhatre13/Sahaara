import React, { useState } from 'react';
import { Send } from 'lucide-react';
import Button from '../common/Button';

export const ChatInput = ({ onSend, disabled }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2 p-3 bg-white border-t border-[#DDE3E8]">
      <textarea
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ask a health question or inquiry..."
        className="flex-1 bg-[#F4F1EC] text-[#1C2733] placeholder-[#8A97A5] text-base rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] resize-none max-h-32 min-h-[48px]"
      />
      <Button
        type="submit"
        variant="primary"
        disabled={disabled || !text.trim()}
        className="h-12 w-12 rounded-xl p-0 flex items-center justify-center shrink-0"
      >
        <Send size={20} />
      </Button>
    </form>
  );
};

export default ChatInput;

