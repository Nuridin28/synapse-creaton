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
 * Преобразует табличные данные (columns, rows) в формат для графиков
 * @param columns - массив названий колонок
 * @param rows - массив объектов с данными строк
 * @returns данные в формате для ChartRenderer
 */
export function convertTableToChartData(columns: string[], rows: any[]): ChartData | null {
  if (!columns || !rows || columns.length === 0 || rows.length === 0) {
    return null;
  }

  // Определяем первую колонку как labels (обычно это категории/даты/названия)
  const labelColumn = columns[0];
  
  // Остальные колонки будут datasets (числовые значения)
  const dataColumns = columns.slice(1).filter(col => {
    // Проверяем, что колонка содержит числовые данные
    return rows.some(row => {
      const value = row[col];
      return value !== null && value !== undefined && !isNaN(Number(value));
    });
  });

  if (dataColumns.length === 0) {
    return null;
  }

  const labels = rows.map(row => String(row[labelColumn] || ''));
  
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

