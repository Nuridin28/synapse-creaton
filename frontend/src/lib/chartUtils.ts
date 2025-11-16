/**
 * Утилиты для преобразования табличных данных в формат графиков
 */

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
  }>;
}

/**
 * Получает все числовые столбцы из таблицы
 */
export function getNumericColumns(columns: string[], rows: any[]): string[] {
  if (!columns || !rows || columns.length === 0 || rows.length === 0) {
    return [];
  }

  return columns.filter(col => {
    // Проверяем, что колонка содержит числовые данные
    return rows.some(row => {
      const value = row[col];
      return value !== null && value !== undefined && !isNaN(Number(value));
    });
  });
}

/**
 * Преобразует табличные данные (columns, rows) в формат для графиков
 * @param columns - массив названий колонок
 * @param rows - массив объектов с данными строк
 * @param selectedColumns - выбранные столбцы для отображения (опционально)
 * @param labelColumn - колонка для labels (опционально, по умолчанию первая)
 * @returns данные в формате для ChartRenderer
 */
export function convertTableToChartData(
  columns: string[], 
  rows: any[], 
  selectedColumns?: string[],
  labelColumn?: string
): ChartData | null {
  if (!columns || !rows || columns.length === 0 || rows.length === 0) {
    return null;
  }

  // Определяем колонку для labels
  const labelCol = labelColumn || columns[0];
  
  // Получаем числовые столбцы
  const numericColumns = getNumericColumns(columns, rows);
  
  // Если указаны выбранные столбцы, используем их, иначе все числовые
  const dataColumns = selectedColumns && selectedColumns.length > 0
    ? selectedColumns.filter(col => numericColumns.includes(col))
    : numericColumns.slice(1); // По умолчанию все кроме первой (которая обычно label)

  if (dataColumns.length === 0) {
    return null;
  }

  const labels = rows.map(row => String(row[labelCol] || ''));
  
  const datasets = dataColumns.map(column => ({
    label: column,
    data: rows.map(row => {
      const value = row[column];
      return value !== null && value !== undefined ? Number(value) : 0;
    }),
  }));

  return {
    labels,
    datasets,
  };
}

