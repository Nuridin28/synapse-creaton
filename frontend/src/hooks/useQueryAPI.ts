import { useState } from 'react';
import { Message } from './useChatHistory';

export function useQueryAPI() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendQuery = async (query: string): Promise<Message> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const json = await response.json();

      if (!json.success) {
        throw new Error(json.error || 'API returned unsuccessful response');
      }

      const results = json.results ?? [];
      const hasData = Array.isArray(results) && results.length > 0;

      // Колонки — это ключи первого объекта
      const columns = hasData ? Object.keys(results[0]) : [];
      // Строки оставляем объектами, чтобы TableRenderer работал с row[column]
      const rows = hasData ? results : [];

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        type: hasData ? 'table' : 'text',
        content: hasData ? 'Query result:' : 'No data returned',
        columns,
        rows,
        timestamp: new Date(),
      };

      return assistantMessage;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to process query';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sendQuery,
    isLoading,
    error,
  };
}
