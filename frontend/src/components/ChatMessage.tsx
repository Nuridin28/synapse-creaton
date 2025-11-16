import { Message } from '@/hooks/useChatHistory';
import { User, Bot } from 'lucide-react';
import { TableRenderer } from './TableRenderer';
import { ChartRenderer } from './ChartRenderer';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-2 sm:gap-4 mb-4 sm:mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-primary flex items-center justify-center">
          <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-primary-foreground" />
        </div>
      )}
      
      <div className={`flex-1 max-w-3xl ${isUser ? 'flex justify-end' : ''}`}>
        <div
          className={`rounded-2xl px-3 py-2 sm:px-4 sm:py-3 ${
            isUser
              ? 'bg-user-message text-white'
              : 'bg-assistant-message border border-border'
          }`}
        >
          {message.type === 'text' && (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          )}
          
          {message.type === 'table' && message.content && (
            <div>
              <p className="text-sm leading-relaxed mb-4">{message.content}</p>
              <TableRenderer columns={message.columns || []} rows={message.rows || []} />
            </div>
          )}
          
          {message.type === 'chart' && message.content && (
            <div>
              <p className="text-sm leading-relaxed mb-4">{message.content}</p>
              <ChartRenderer
                type={message.chartType || 'line'}
                data={message.chartData}
              />
            </div>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-muted flex items-center justify-center">
          <User className="w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
        </div>
      )}
    </div>
  );
}
