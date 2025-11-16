import { Bot } from 'lucide-react';

export function LoadingMessage() {
  return (
    <div className="flex gap-2 sm:gap-4 mb-4 sm:mb-6">
      <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-primary flex items-center justify-center">
        <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-primary-foreground" />
      </div>
      
      <div className="flex-1 max-w-3xl">
        <div className="rounded-2xl px-3 py-2 sm:px-4 sm:py-3 bg-assistant-message border border-border">
          <div className="flex gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
