import { useState } from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  type: 'text' | 'table' | 'chart';
  content?: string;
  columns?: string[];
  rows?: any[];
  chartType?: 'line' | 'bar' | 'pie';
  chartData?: any;
  timestamp: Date;
}

export function useChatHistory() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  };

  const clearHistory = () => {
    setMessages([]);
  };

  return {
    messages,
    addMessage,
    clearHistory,
    isLoading,
    setIsLoading,
  };
}
