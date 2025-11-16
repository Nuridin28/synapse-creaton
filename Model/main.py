"""
Main entry point for SQL Query Generator.

This is the primary interface for the SQL Query Generator system.
It provides a command-line interface for generating SQL queries from natural language.
"""

import sys
import argparse
from sql_generator import SQLQueryGenerator


def main():
    """Main entry point for SQL Query Generator."""
    
    parser = argparse.ArgumentParser(
        description="SQL Query Generator - Convert natural language to SQL SELECT queries"
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        default="example_dataset.parquet",
        help="Path to the parquet dataset file (default: example_dataset.parquet)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="NousResearch/Nous-Hermes-llama-2-7b",
        help="Hugging Face model name or local path (default: NousResearch/Nous-Hermes-llama-2-7b)"
    )
    
    parser.add_argument(
        "--no-quantization",
        action="store_true",
        help="Disable 8-bit quantization (uses more memory but may be faster)"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Single query to process (non-interactive mode)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="Run in interactive mode (default)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    print("Initializing SQL Query Generator...")
    try:
        generator = SQLQueryGenerator(
            dataset_path=args.dataset,
            model_name=args.model,
            use_quantization=not args.no_quantization,
            device_map="auto"
        )
        print("Generator initialized successfully!\n")
    except Exception as e:
        print(f"Error initializing generator: {str(e)}")
        sys.exit(1)
    
    # Single query mode
    if args.query:
        sql = generator.generate(args.query)
        print(sql)
        return
    
    # Interactive mode
    if args.interactive:
        print("=" * 60)
        print("SQL Query Generator - Interactive Mode")
        print("=" * 60)
        print("Type your natural language questions to generate SQL queries.")
        print("Commands:")
        print("  'clear' - Clear conversation history")
        print("  'quit' or 'exit' - Exit the program")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("Question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'clear':
                    generator.clear_history()
                    print("Conversation history cleared.\n")
                    continue
                
                # Generate SQL
                sql_query = generator.generate(user_input)
                print(f"\n{sql_query}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()

