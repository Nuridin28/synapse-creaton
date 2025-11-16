---
title: SQL Query Generator
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# SQL Query Generator - Nuraly Business Transaction Dataset

An advanced SQL Query Generator that converts natural language questions into **safe, correct, well-structured SQL SELECT queries only**.

## 🚀 Features

- **Safe SQL Generation**: Only generates SELECT queries, never destructive operations
- **Schema-Aware**: Uses exact column and table names from the training dataset (`example_dataset.parquet`)
- **Conversation History**: Supports context-aware queries with "now show me..." patterns
- **Input Validation**: Protects against harmful user input and politely refuses unsafe requests
- **Multi-Language Support**: Accepts questions in any language, but generates SQL in English only
- **English-Only Output**: All SQL queries, values, column names, and string literals are in English
- **Nous-Hermes-Llama2-7b Based**: Built on Nous-Hermes-Llama2-7b model (open source, fine-tuned for instruction following)

## 📋 Rules

The system follows strict rules:

1. Always output ONLY SQL SELECT queries
2. NEVER generate DROP, DELETE, UPDATE, INSERT, ALTER, or TRUNCATE
3. Use only the exact column names and table names from the schema
4. Understand filtering conditions, numerical ranges, categories, amounts, OR/AND logic, date ranges, aggregates, grouping, sorting
5. Always protect the database from harmful user input
6. If the user asks for something unsafe, politely refuse
7. Support conversation history (e.g., "now show me..." continues from previous query)
8. If the question is ambiguous, ask for clarification
9. Output no explanations — SQL ONLY
10. **CRITICAL**: The entire SQL query MUST be in English, regardless of the language of the user's question
    - ALL SQL keywords must be in English: SELECT, FROM, WHERE, AND, OR, etc.
    - ALL values in the query MUST be in English, exactly as they appear in the database
    - ALL string literals (city names, categories, etc.) MUST be in English
    - Example: If user asks 'Посчитай сколько в Алмате', use 'Almaty' (not 'Алматы' or 'Алмата')

## 🎯 Usage

### Hugging Face Spaces

This app is deployed on Hugging Face Spaces. Simply:
1. Wait for the model to load (this may take a few minutes on first run)
2. Type your question in any language
3. The system will generate a SQL query with all values in English
4. Use "Clear History" to start a new conversation

### Local Installation

```bash
pip install -r requirements.txt
```

### Command Line Interface

```bash
# Interactive mode (default)
python main.py

# Single query mode
python main.py --query "Show me all transactions above $1000"

# Custom dataset
python main.py --dataset path/to/your_dataset.parquet
```

### Python API

```python
from sql_generator import SQLQueryGenerator

# Initialize the generator
generator = SQLQueryGenerator(
    dataset_path="example_dataset.parquet",
    model_name="NousResearch/Nous-Hermes-llama-2-7b",
    use_quantization=True  # Use 8-bit quantization to save memory
)

# Generate SQL from natural language
query = generator.generate("Show me all transactions above $1000")
print(query)
# Output: SELECT * FROM example_dataset WHERE amount > 1000;
```

### With Conversation History

```python
# First query
query1 = generator.generate("Show me transactions from January 2024")
print(query1)

# Follow-up query with context
query2 = generator.generate("now show me only those above $500")
print(query2)  # This will build on the previous query

# Clear history if needed
generator.clear_history()
```

## 📊 Dataset

Place your `example_dataset.parquet` file in the project root. The system will automatically:
- Analyze the schema (table name, columns, data types)
- Extract sample data for context
- Use this information to generate accurate SQL queries

## 🔒 Safety Features

- **Only SELECT queries**: All other SQL operations are blocked
- **Input sanitization**: Detects and blocks SQL injection attempts
- **Query validation**: Validates generated SQL before returning
- **Politely refuses**: Returns error comments for unsafe requests instead of executing them

## 🤖 Model

Uses **Nous-Hermes-Llama2-7b** model (open source, fine-tuned for instruction following), which can be:
- Loaded from Hugging Face: `NousResearch/Nous-Hermes-llama-2-7b` (no special access required)
- Loaded from a local fine-tuned checkpoint (specify path in `model_name`)

The model is optimized with 8-bit quantization by default to reduce memory usage. Nous-Hermes-Llama2-7b is fully open source and freely available. It's a fine-tuned version of LLaMA-2, optimized for instruction following tasks like SQL generation.

## 📤 Output Format

The system returns **SQL ONLY** - no explanations, no markdown, just the SQL query:

```sql
SELECT COUNT(*) FROM example_dataset WHERE city = 'Almaty' AND date >= '2023-11-01' AND date < '2023-12-01';
```

For errors or clarifications, SQL comments are used:

```sql
-- ERROR: Input contains potentially dangerous pattern
-- Please clarify your question. The request is ambiguous.
```

## 🏗️ Architecture

- `app.py`: Gradio interface for Hugging Face Spaces
- `sql_generator.py`: Main SQL generation logic using Nous-Hermes-Llama2-7b
- `schema_analyzer.py`: Analyzes parquet dataset to extract schema
- `safety_validator.py`: Validates SQL queries and sanitizes input
- `conversation_manager.py`: Manages conversation history for context-aware queries
- `main.py`: Command-line interface

## 🌍 Multi-Language Support

The system accepts questions in any language but always generates SQL queries in English:

- **Question (Russian)**: "Посчитай сколько в Алмате в ноябре 2023 произошло транзакций"
- **Generated SQL (English)**: `SELECT COUNT(*) FROM example_dataset WHERE merchant_city = 'Almaty' AND transaction_timestamp >= '2023-11-01' AND transaction_timestamp < '2023-12-01';`

All values are automatically translated to their English equivalents from the database schema.

## 📝 Examples

- "Show me all transactions above $1000"
- "Посчитай сколько в Алмате в ноябре 2023 произошло транзакций"
- "What is the total amount of transactions by category?"
- "Show me transactions between $500 and $2000"
- "now show me only those from January 2024"

## 📄 License

MIT License
