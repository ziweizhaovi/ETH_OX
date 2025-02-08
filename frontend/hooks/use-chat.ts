import { useState } from 'react';

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface TradeContext {
  operation_type: 'buy' | 'sell' | 'analyze';
  amount?: number;
  token_pair: 'AVAX/USDC';
  slippage_tolerance?: number;
}

export interface ChatMessage {
  message: string;
  context?: TradeContext;
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (chatMessage: ChatMessage) => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('Sending message:', chatMessage);

      // Add user message to the chat
      setMessages(prev => [...prev, { role: 'user', content: chatMessage.message }]);

      // Send message to backend
      const response = await fetch('http://localhost:8000/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatMessage),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();
      console.log('Received data:', data);
      
      // Add assistant's response to the chat
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);

      return data;
    } catch (err) {
      console.error('Error in sendMessage:', err);
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      setMessages(prev => [...prev, { role: 'system', content: `Error: ${errorMessage}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8000/api/v1/ai/clear', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to clear chat history');
      }

      setMessages([]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
}; 