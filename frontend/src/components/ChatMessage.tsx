import { Message } from '@/hooks/useChatHistory';
import { User, Bot, Table2, LineChart, BarChart3, PieChart, Settings2 } from 'lucide-react';
import { TableRenderer } from './TableRenderer';
import { ChartRenderer } from './ChartRenderer';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { convertTableToChartData, getNumericColumns } from '@/lib/chartUtils';
import { useI18n } from '@/contexts/I18nContext';

interface ChatMessageProps {
  message: Message;
  onViewModeChange?: (messageId: string, viewMode: 'table' | 'line' | 'bar' | 'pie') => void;
  onSelectedColumnsChange?: (messageId: string, selectedColumns: string[]) => void;
}

export function ChatMessage({ message, onViewModeChange, onSelectedColumnsChange }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const { t } = useI18n();
  const hasTableData = message.type === 'table' && message.columns && message.rows && message.columns.length > 0 && message.rows.length > 0;
  const currentViewMode = message.viewMode || 'table';
  
  // Получаем числовые столбцы
  const numericColumns = hasTableData ? getNumericColumns(message.columns!, message.rows!) : [];
  const labelColumn = hasTableData ? message.columns![0] : '';
  
  // Выбранные столбцы (по умолчанию все числовые кроме первой)
  const defaultSelectedColumns = numericColumns.length > 1 ? numericColumns.slice(1) : numericColumns;
  const selectedColumns = message.selectedColumns && message.selectedColumns.length > 0 
    ? message.selectedColumns 
    : defaultSelectedColumns;
  
  // Преобразуем табличные данные в формат для графиков
  const chartData = hasTableData 
    ? convertTableToChartData(message.columns!, message.rows!, selectedColumns, labelColumn)
    : null;
  const canShowCharts = chartData !== null && selectedColumns.length > 0;

  const handleViewModeChange = (viewMode: 'table' | 'line' | 'bar' | 'pie') => {
    if (onViewModeChange) {
      onViewModeChange(message.id, viewMode);
    }
  };

  const handleColumnToggle = (column: string, checked: boolean) => {
    if (!onSelectedColumnsChange) return;
    
    const newSelected = checked
      ? [...selectedColumns, column]
      : selectedColumns.filter(col => col !== column);
    
    // Минимум один столбец должен быть выбран
    if (newSelected.length > 0) {
      onSelectedColumnsChange(message.id, newSelected);
    }
  };

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
          
          {hasTableData && (
            <div>
              {message.content && (
                <p className="text-sm leading-relaxed mb-4">{message.content}</p>
              )}
              
              {/* Кнопки переключения формата и выбора столбцов */}
              {canShowCharts && (
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <ToggleGroup
                    type="single"
                    value={currentViewMode}
                    onValueChange={(value) => {
                      if (value && (value === 'table' || value === 'line' || value === 'bar' || value === 'pie')) {
                        handleViewModeChange(value);
                      }
                    }}
                    className="flex flex-wrap gap-1"
                  >
                    <ToggleGroupItem
                      value="table"
                      aria-label={t.viewMode.table}
                      className="text-xs sm:text-sm"
                    >
                      <Table2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span className="hidden sm:inline">{t.viewMode.table}</span>
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      value="line"
                      aria-label={t.viewMode.line}
                      className="text-xs sm:text-sm"
                    >
                      <LineChart className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span className="hidden sm:inline">{t.viewMode.line}</span>
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      value="bar"
                      aria-label={t.viewMode.bar}
                      className="text-xs sm:text-sm"
                    >
                      <BarChart3 className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span className="hidden sm:inline">{t.viewMode.bar}</span>
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      value="pie"
                      aria-label={t.viewMode.pie}
                      className="text-xs sm:text-sm"
                    >
                      <PieChart className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span className="hidden sm:inline">{t.viewMode.pie}</span>
                    </ToggleGroupItem>
                  </ToggleGroup>
                  
                  {/* Кнопка выбора столбцов */}
                  {currentViewMode !== 'table' && numericColumns.length > 1 && (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-xs sm:text-sm h-8"
                        >
                          <Settings2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                          <span className="hidden sm:inline">{t.viewMode.selectColumns}</span>
                          <span className="sm:hidden">{t.viewMode.columns}</span>
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-56 p-3" align="start">
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium mb-2">{t.viewMode.selectColumns}</h4>
                          <div className="space-y-2 max-h-60 overflow-y-auto">
                            {numericColumns.map((column) => (
                              <div key={column} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`column-${message.id}-${column}`}
                                  checked={selectedColumns.includes(column)}
                                  onCheckedChange={(checked) => 
                                    handleColumnToggle(column, checked === true)
                                  }
                                  disabled={selectedColumns.length === 1 && selectedColumns.includes(column)}
                                />
                                <label
                                  htmlFor={`column-${message.id}-${column}`}
                                  className="text-sm font-normal cursor-pointer flex-1"
                                >
                                  {column}
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </PopoverContent>
                    </Popover>
                  )}
                </div>
              )}
              
              {/* Отображение выбранного формата */}
              {currentViewMode === 'table' && (
                <TableRenderer columns={message.columns || []} rows={message.rows || []} />
              )}
              
              {currentViewMode === 'line' && chartData && (
                <ChartRenderer type="line" data={chartData} />
              )}
              
              {currentViewMode === 'bar' && chartData && (
                <ChartRenderer type="bar" data={chartData} />
              )}
              
              {currentViewMode === 'pie' && chartData && (
                <ChartRenderer type="pie" data={chartData} />
              )}
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
