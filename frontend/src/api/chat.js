import client from './client';

export const askChatbot = async (userId, sessionId, message) => {
  const response = await client.post('/chat/ask', {
    user_id: userId,
    session_id: sessionId,
    message: message,
  });
  return response.data;
};

export const getSessionMessages = async (sessionId) => {
  const response = await client.get(`/chat/session/${sessionId}/messages`);
  return response.data;
};

