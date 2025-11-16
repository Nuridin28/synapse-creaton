import { useState, useRef, useEffect } from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from '@/components/ChatMessage';
import { LoadingMessage } from '@/components/LoadingMessage';
import { InputArea } from '@/components/InputArea';
import { AnalyticsSidebar } from '@/components/AnalyticsSidebar';
import { ThemeToggle } from '@/components/ThemeToggle';
import { LanguageToggle } from '@/components/LanguageToggle';
import { useChatHistory } from '@/hooks/useChatHistory';
import { useQueryAPI } from '@/hooks/useQueryAPI';
import { useToast } from '@/hooks/use-toast';
import { useI18n } from '@/contexts/I18nContext';

const Index = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { messages, addMessage, isLoading, setIsLoading } = useChatHistory();
  const { sendQuery } = useQueryAPI();
  const { toast } = useToast();
  const { t } = useI18n();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSendMessage = async (query: string) => {
    // Add user message
    addMessage({
      role: 'user',
      type: 'text',
      content: query,
    });

    setIsLoading(true);

    try {
      // Send query to API
      const assistantMessage = await sendQuery(query);
      addMessage(assistantMessage);
      console.log(assistantMessage)

    } catch (error) {
      toast({
        title: t.error.title,
        description: t.error.description,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateClick = (template: string) => {
    handleSendMessage(template);
  };

  return (
    <div className="flex h-screen w-full bg-background">
      <AnalyticsSidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        onTemplateClick={handleTemplateClick}
      />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="border-b border-border bg-card px-3 sm:px-6 py-3 sm:py-4 flex items-center gap-3 sm:gap-4">
          {isSidebarCollapsed && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarCollapsed(false)}
              className="h-8 w-8"
            >
              <Menu className="h-4 w-4" />
            </Button>
          )}
          <div className="min-w-0 flex-1">
            <h1 className="text-base sm:text-lg font-semibold text-foreground truncate">{t.header.title}</h1>
            <p className="text-xs sm:text-sm text-muted-foreground truncate">{t.header.subtitle}</p>
          </div>
          <div className="flex items-center gap-2">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </header>

        {/* Chat area */}
        <ScrollArea className="flex-1 p-3 sm:p-6" ref={scrollRef}>
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && !isLoading && (
              <div className="text-center py-8 sm:py-12 px-4">
                <div className="inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-primary/10 mb-3 sm:mb-4">
                  <svg
                    className="w-6 h-6 sm:w-8 sm:h-8 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h2 className="text-lg sm:text-xl font-semibold mb-2">{t.welcome.title}</h2>
                <p className="text-sm sm:text-base text-muted-foreground max-w-md mx-auto">
                  {t.welcome.description}
                </p>
              </div>
            )}

            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {isLoading && <LoadingMessage />}
          </div>
        </ScrollArea>

        {/* Input area */}
        <InputArea onSend={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default Index;
