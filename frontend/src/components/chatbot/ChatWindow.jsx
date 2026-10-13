import React, { useEffect, useRef } from 'react';
import ChatMessageBubble from './ChatMessageBubble';
import { motion } from 'framer-motion';

export const ChatWindow = ({ messages = [], isThinking }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 ? (
        <div className="text-center py-12 text-[#8A97A5]">
          <p className="text-lg font-bold text-[#1C2733] mb-1">Hello! How can I assist your health today?</p>
          <p className="text-sm">Ask about symptoms, medication guidance, or healthy elder habits.</p>
        </div>
      ) : (
        messages.map((msg, idx) => <ChatMessageBubble key={idx} message={msg} />)
      )}

      {/* Thinking dots indicator */}
      {isThinking && (
        <div className="flex items-center gap-2 text-[#8A97A5] text-sm p-3 bg-white rounded-2xl border border-[#DDE3E8] w-fit">
          <span>Sahaara Assistant is thinking</span>
          <span className="flex items-center gap-1">
            <motion.span
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0 }}
              className="w-2 h-2 rounded-full bg-[#1E3A5F]"
            />
            <motion.span
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
              className="w-2 h-2 rounded-full bg-[#1E3A5F]"
            />
            <motion.span
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
              className="w-2 h-2 rounded-full bg-[#1E3A5F]"
            />
          </span>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;

