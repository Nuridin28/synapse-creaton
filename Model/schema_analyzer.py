"""
Schema Analyzer for extracting table and column information from parquet dataset.
"""
import pandas as pd
import pyarrow.parquet as pq
from typing import Dict, List, Tuple
import json


class SchemaAnalyzer:
    """Analyzes parquet file to extract schema information for SQL generation."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize schema analyzer.
        
        Args:
            dataset_path: Path to the parquet file
        """
        self.dataset_path = dataset_path
        self.schema_info = None
        self.table_name = None
        self.columns = None
        self.column_types = None
        self.sample_data = None
        
    def analyze(self) -> Dict:
        """
        Analyze the parquet file and extract schema information.
        
        Returns:
            Dictionary containing schema information
        """
        try:
            # Read parquet file
            df = pd.read_parquet(self.dataset_path)
            
            # Extract table name (from filename or default)
            self.table_name = self._extract_table_name()
            
            # Extract column information
            self.columns = list(df.columns)
            self.column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            # Get sample data for understanding data patterns
            self.sample_data = df.head(10).to_dict('records')
            
            # Build schema info
            self.schema_info = {
                'table_name': self.table_name,
                'columns': self.columns,
                'column_types': self.column_types,
                'row_count': len(df),
                'sample_data': self.sample_data[:5]  # First 5 rows for context
            }
            
            return self.schema_info
            
        except Exception as e:
            raise ValueError(f"Error analyzing dataset: {str(e)}")
    
    def _extract_table_name(self) -> str:
        """Extract table name from file path or use default."""
        import os
        filename = os.path.basename(self.dataset_path)
        # Remove extension and use as table name
        table_name = os.path.splitext(filename)[0]
        # Replace hyphens/underscores with underscores, make lowercase
        table_name = table_name.replace('-', '_').replace(' ', '_').lower()
        return table_name if table_name else 'transactions'
    
    def get_schema_prompt(self) -> str:
        """
        Generate a schema description for the model prompt.
        
        Returns:
            Formatted schema description string
        """
        if not self.schema_info:
            self.analyze()
        
        schema_parts = [
            f"TABLE: {self.schema_info['table_name']}",
            f"COLUMNS: {', '.join(self.schema_info['columns'])}",
            "COLUMN TYPES:"
        ]
        
        for col, dtype in self.schema_info['column_types'].items():
            schema_parts.append(f"  - {col}: {dtype}")
        
        # Add example values for important columns (especially city names, dates, etc.)
        if self.sample_data:
            schema_parts.append("")
            schema_parts.append("EXAMPLE VALUES (use these exact English values in queries):")
            
            # Extract unique example values for each column
            example_values = {}
            for record in self.sample_data[:10]:  # Use up to 10 sample records
                for col, value in record.items():
                    if value is not None and str(value).strip():
                        if col not in example_values:
                            example_values[col] = set()
                        example_values[col].add(str(value))
            
            # Show examples for key columns (especially city, date columns)
            for col in self.columns:
                if col in example_values and len(example_values[col]) > 0:
                    examples = list(example_values[col])[:5]  # Show up to 5 examples
                    if examples:
                        schema_parts.append(f"  - {col}: {', '.join(examples)}")
        
        return "\n".join(schema_parts)
    
    def get_schema_json(self) -> str:
        """Get schema as JSON string."""
        if not self.schema_info:
            self.analyze()
        return json.dumps(self.schema_info, indent=2)

