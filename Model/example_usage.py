"""
Example usage of the SQL Query Generator.

This script demonstrates how to use the SQL Query Generator
to convert natural language questions into SQL SELECT queries.
"""

from sql_generator import SQLQueryGenerator


def main():
    """Example usage of SQL Query Generator."""
    
    print("=" * 60)
    print("SQL Query Generator - Example Usage")
    print("=" * 60)
    print()
    
    # Initialize the generator
    print("Initializing SQL Query Generator...")
    print("(This may take a few minutes to load the model)")
    print()
    
    try:
        generator = SQLQueryGenerator(
            dataset_path="example_dataset.parquet",
            model_name="NousResearch/Nous-Hermes-llama-2-7b",
            use_quantization=True,  # Use 8-bit quantization to save memory
            device_map="auto"
        )
        
        print("\n" + "=" * 60)
        print("Generator ready! You can now ask questions.")
        print("=" * 60)
        print()
        
        # Example queries
        example_queries = [
            "Show me all transactions above $1000",
            "now show me only those from January 2024",
            "What is the total amount of transactions by category?",
            "Show me transactions between $500 and $2000",
        ]
        
        print("Example queries:")
        for i, query in enumerate(example_queries, 1):
            print(f"\n{i}. User: {query}")
            sql = generator.generate(query)
            print(f"   SQL: {sql}")
        
        print("\n" + "=" * 60)
        print("Interactive mode - Type your questions (or 'quit' to exit)")
        print("=" * 60)
        print()
        
        # Interactive mode
        while True:
            user_input = input("Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            # Generate SQL
            sql_query = generator.generate(user_input)
            print(f"\nGenerated SQL:\n{sql_query}\n")
            
            # Option to clear history
            if user_input.lower() == 'clear':
                generator.clear_history()
                print("Conversation history cleared.\n")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed all requirements: pip install -r requirements.txt")
        print("2. The example_dataset.parquet file in the project directory")
        print("3. Internet connection to download the Nous-Hermes-Llama2-7b model (open source, no token required)")


if __name__ == "__main__":
    main()

