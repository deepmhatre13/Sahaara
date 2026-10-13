import React from 'react';
import { motion } from 'framer-motion';
import ChatSourcesFooter from './ChatSourcesFooter';
import { Bot, User } from 'lucide-react';

export const ChatMessageBubble = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 my-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
          isUser ? 'bg-[#1E3A5F] text-white' : 'bg-[#D98E4A] text-white'
        }`}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div
        className={`max-w-[80%] rounded-2xl p-4 text-base leading-relaxed ${
          isUser
            ? 'bg-[#1E3A5F] text-white rounded-tr-none'
            : 'bg-white text-[#1C2733] border border-[#DDE3E8] rounded-tl-none shadow-xs'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content || message.text}</p>
        {!isUser && message.sources && <ChatSourcesFooter sources={message.sources} />}
      </div>
    </motion.div>
  );
};

export default ChatMessageBubble;

