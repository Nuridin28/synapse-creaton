import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface TableRendererProps {
  columns: string[];
  rows: any[];
}

export function TableRenderer({ columns, rows }: TableRendererProps) {
  if (!columns.length || !rows.length) {
    return <p className="text-sm text-muted-foreground">No data available</p>;
  }

  return (
    <div className="rounded-lg border border-border overflow-x-auto bg-card">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50">
            {columns.map((column, index) => (
              <TableHead key={index} className="font-semibold whitespace-nowrap text-xs sm:text-sm">
                {column}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, rowIndex) => (
            <TableRow key={rowIndex} className="hover:bg-muted/30">
              {columns.map((column, colIndex) => (
                <TableCell key={colIndex} className="whitespace-nowrap text-xs sm:text-sm">{row[column]}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
