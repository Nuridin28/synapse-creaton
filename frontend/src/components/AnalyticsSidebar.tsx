import { History, Sparkles, FileText, ChevronLeft, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useI18n } from '@/contexts/I18nContext';

interface AnalyticsSidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  onTemplateClick: (template: string) => void;
}

export function AnalyticsSidebar({ isCollapsed, onToggle, onTemplateClick }: AnalyticsSidebarProps) {
  const { t } = useI18n();

  const queryTemplates = [
    { icon: Sparkles, label: t.sidebar.templates.salesOverview, query: t.input.examplePrompts[0] },
    { icon: FileText, label: t.sidebar.templates.revenueAnalysis, query: t.input.examplePrompts[1] },
    { icon: History, label: t.sidebar.templates.customerGrowth, query: t.input.examplePrompts[2] },
    { icon: Sparkles, label: t.sidebar.templates.topProducts, query: t.input.examplePrompts[3] },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {!isCollapsed && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onToggle}
        />
      )}
      
      <div
        className={`bg-sidebar border-r border-sidebar-border transition-all duration-300 
          fixed md:relative h-full z-50 md:z-0
          ${isCollapsed ? '-left-64' : 'left-0'} md:left-0
          ${isCollapsed ? 'md:w-0 md:overflow-hidden' : 'w-64'}
        `}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 flex items-center justify-between">
            <h2 className="font-semibold text-sidebar-foreground">{t.sidebar.title}</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="h-8 w-8"
            >
              <ChevronLeft className="h-4 w-4 hidden md:block" />
              <X className="h-4 w-4 md:hidden" />
            </Button>
          </div>

        <Separator className="bg-sidebar-border" />

        <ScrollArea className="flex-1">
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-semibold text-muted-foreground mb-3 px-2">
                  {t.sidebar.quickQueries}
                </h3>
                <div className="space-y-1">
                  {queryTemplates.map((template, index) => (
                    <Button
                      key={index}
                      variant="ghost"
                      className="w-full justify-start text-sm hover:bg-sidebar-accent"
                      onClick={() => onTemplateClick(template.query)}
                    >
                      <template.icon className="mr-2 h-4 w-4" />
                      {template.label}
                    </Button>
                  ))}
                </div>
              </div>

              <Separator className="bg-sidebar-border" />

              <div>
                <h3 className="text-xs font-semibold text-muted-foreground mb-3 px-2">
                  {t.sidebar.recentQueries}
                </h3>
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm text-left hover:bg-sidebar-accent"
                  >
                    <History className="mr-2 h-4 w-4 flex-shrink-0" />
                    <span className="truncate">{t.sidebar.recent.salesTrends}</span>
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm text-left hover:bg-sidebar-accent"
                  >
                    <History className="mr-2 h-4 w-4 flex-shrink-0" />
                    <span className="truncate">{t.sidebar.recent.customerData}</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
    </>
  );
}
