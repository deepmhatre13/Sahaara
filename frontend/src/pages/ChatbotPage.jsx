import React, { useState } from 'react';
import useAuth from '../hooks/useAuth';
import { askChatbot } from '../api/chat';
import ChatWindow from '../components/chatbot/ChatWindow';
import ChatInput from '../components/chatbot/ChatInput';
import Button from '../components/common/Button';
import { Bot, RefreshCw, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export const ChatbotPage = () => {
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);

  const handleSend = async (userMessage) => {
    if (!user?.id) return;
    const newMsg = { role: 'user', content: userMessage };
    setMessages((prev) => [...prev, newMsg]);
    setIsThinking(true);

    try {
      const res = await askChatbot(user.id, sessionId, userMessage);
      const assistantMsg = {
        role: 'assistant',
        content: res.response || res.message,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      toast.error('Failed to receive AI response. Please try again.');
    } finally {
      setIsThinking(false);
    }
  };

  const handleNewSession = () => {
    setSessionId(`session_${Date.now()}`);
    setMessages([]);
    toast.success('Started a new conversation session');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-4xl mx-auto bg-white rounded-2xl border border-[#DDE3E8] overflow-hidden shadow-sm">
      {/* Header with Persistent Disclaimer */}
      <div className="p-4 border-b border-[#DDE3E8] bg-[#F4F1EC]/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#D98E4A] text-white rounded-xl">
            <Bot size={22} />
          </div>
          <div>
            <h3 className="font-bold text-[#1C2733] text-lg">AI Health Assistant</h3>
            <div className="flex items-center gap-1.5 text-xs text-[#8A97A5] mt-0.5">
              <AlertCircle size={14} className="text-[#D98E4A]" />
              <span>General information only — not medical advice</span>
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handleNewSession}
          className="flex items-center gap-1.5 text-xs self-start sm:self-auto"
        >
          <RefreshCw size={14} />
          <span>New Session</span>
        </Button>
      </div>

      {/* Messages Scroll Area */}
      <ChatWindow messages={messages} isThinking={isThinking} />

      {/* Fixed Chat Input */}
      <ChatInput onSend={handleSend} disabled={isThinking} />
    </div>
  );
};

export default ChatbotPage;
