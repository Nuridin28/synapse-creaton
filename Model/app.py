"""
Gradio app for SQL Query Generator - Hugging Face Spaces deployment.
"""
import gradio as gr
import os
import sys
from sql_generator import SQLQueryGenerator
import subprocess

# Global variable to store the generator
generator = None
from spaces import GPU
print("🔄 Загрузка LFS файлов...")
try:
    # Скачиваем LFS файлы
    result = subprocess.run(
        ["git", "lfs", "pull"], 
        capture_output=True, 
        text=True,
        timeout=60  # 60 секунд таймаут
    )
    if result.returncode == 0:
        print("✅ LFS файлы успешно загружены!")
        if os.path.exists("example_dataset.parquet"):
            file_size = os.path.getsize("example_dataset.parquet") / (1024 * 1024)
            print(f"📊 Dataset загружен: {file_size:.1f} MB")
        else:
            print("❌ Файл dataset не найден после LFS pull")
    else:
        print(f"⚠️ LFS ошибка: {result.stderr}")
except subprocess.TimeoutExpired:
    print("⏰ Таймаут загрузки LFS файлов")
except Exception as e:
    print(f"❌ Ошибка LFS: {e}")

# Проверяем существование файла
if os.path.exists("example_dataset.parquet"):
    print("🎯 Dataset готов к использованию!")
else:
    print("❌ Dataset не доступен, будут использоваться fallback данные")

@GPU
def dummy_gpu_function():
    # Пустая функция только для инициализации GPU
    return "GPU initialized"

# Вызовите один раз при запуске
dummy_gpu_function()

def initialize_generator():
    """Initialize the SQL Query Generator."""
    global generator
    if generator is None:
        print("Initializing SQL Query Generator...")
        try:
            dataset_path = os.getenv("DATASET_PATH", "example_dataset.parquet")
            model_name = os.getenv("MODEL_NAME", "NousResearch/Nous-Hermes-llama-2-7b")
            use_quantization = os.getenv("USE_QUANTIZATION", "true").lower() == "true"
            
            print("Loading dataset schema...")
            generator = SQLQueryGenerator(
                dataset_path=dataset_path,
                model_name=model_name,
                use_quantization=use_quantization,
                device_map="auto"
            )
            print("Initialization complete!")
            print("SQL Query Generator initialized successfully!")
            return "✅ SQL Query Generator initialized successfully!"
        except Exception as e:
            error_msg = f"❌ Error initializing generator: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg
    return "✅ SQL Query Generator already initialized!"

def generate_sql(question, history):
    """Generate SQL query from natural language question."""
    global generator
    
    # Initialize history if None or not a list
    if history is None:
        history = []
    elif not isinstance(history, list):
        history = []
    
    # Check if generator is initialized
    if generator is None:
        error_msg = "⚠️ Please wait for the model to load. This may take a few minutes on first run."
        history.append(("", error_msg))
        return "", history
    
    # Validate and clean question input
    if question is None:
        question = ""
    
    # Strip whitespace and check if empty
    question = str(question).strip()
    
    if not question:
        error_msg = "⚠️ Please enter a question."
        # Don't add empty question to history, just return
        return "", history
    
    try:
        # Generate SQL query
        print(f"Processing question: {question}")
        sql_query = generator.generate(question)
        print(f"Generated SQL: {sql_query}")
        
        # Update conversation history
        history.append((question, sql_query))
        
        # Return empty string for question input (to clear it) and updated history
        return "", history
    except Exception as e:
        error_msg = f"-- ERROR: {str(e)}"
        print(f"Error generating SQL: {error_msg}")
        import traceback
        traceback.print_exc()
        # Add error to history
        history.append((question, error_msg))
        return "", history

def clear_conversation():
    """Clear conversation history."""
    global generator
    if generator is not None:
        generator.clear_history()
    return []

def get_schema_info():
    """Get schema information for display."""
    global generator
    if generator is None:
        return "⚠️ Please wait for the model to load first."
    
    try:
        schema_info = generator.get_schema_info()
        info_text = f"**Table:** {schema_info['table_name']}\n\n"
        info_text += f"**Columns:** {', '.join(schema_info['columns'])}\n\n"
        info_text += "**Column Types:**\n"
        for col, dtype in schema_info['column_types'].items():
            info_text += f"- {col}: {dtype}\n"
        info_text += f"\n**Total Rows:** {schema_info['row_count']}"
        return info_text
    except Exception as e:
        return f"Error getting schema info: {str(e)}"

# Custom CSS for better UI
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.sql-output {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
}
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, title="SQL Query Generator") as demo:
    gr.Markdown("""
    # 🔍 SQL Query Generator
    
    Convert natural language questions into **safe, correct SQL SELECT queries**.
    
    **Features:**
    - ✅ Safe SQL generation (SELECT queries only)
    - ✅ Schema-aware (uses exact column and table names from dataset)
    - ✅ Conversation history support
    - ✅ English-only output (all values in English, regardless of question language)
    - ✅ Multi-language question support
    
    **Instructions:**
    1. Wait for the model to load (this may take a few minutes on first run)
    2. Type your question in any language
    3. The system will generate a SQL query with all values in English
    4. Use "Clear History" to start a new conversation
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Schema Information")
            schema_display = gr.Markdown(value="Click 'Load Schema' to view schema information.")
            load_schema_btn = gr.Button("📋 Load Schema", variant="secondary")
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat Interface")
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_copy_button=True,
                avatar_images=(None, "🤖"),
                value=[]  # Initialize with empty list
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask a question in any language (e.g., 'Посчитай сколько в Алмате в ноябре 2023 произошло транзакций')",
                    lines=2,
                    scale=4
                )
                submit_btn = gr.Button("🚀 Generate SQL", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear History", variant="secondary")
                init_btn = gr.Button("⚙️ Initialize Model", variant="secondary")
    
    gr.Markdown("""
    ### 📝 Examples
    
    - "Show me all transactions above $1000"
    - "Посчитай сколько в Алмате в ноябре 2023 произошло транзакций"
    - "What is the total amount of transactions by category?"
    - "Show me transactions between $500 and $2000"
    
    ### ⚠️ Important Notes
    
    - All SQL queries are generated in **English only**
    - All values (city names, categories, etc.) are converted to English from the database
    - Only SELECT queries are allowed (safe operations only)
    - The model uses 8-bit quantization for efficient memory usage
    """)
    
    # Event handlers
    init_btn.click(
        fn=initialize_generator,
        outputs=gr.Textbox(visible=False),
        show_progress=True
    )
    
    load_schema_btn.click(
        fn=get_schema_info,
        outputs=schema_display,
        show_progress=True
    )
    
    def handle_submit(question, history):
        """Wrapper to handle submit with proper input validation."""
        # Ensure history is a list
        if history is None:
            history = []
        # Ensure question is a string
        if question is None:
            question = ""
        return generate_sql(question, history)
    
    submit_btn.click(
        fn=handle_submit,
        inputs=[question_input, chatbot],
        outputs=[question_input, chatbot],
        show_progress=True
    )
    
    question_input.submit(
        fn=handle_submit,
        inputs=[question_input, chatbot],
        outputs=[question_input, chatbot],
        show_progress=True
    )
    
    clear_btn.click(
        fn=clear_conversation,
        outputs=chatbot,
        show_progress=False
    )
    
    # Initialize on load (with error handling)
    demo.load(
        fn=lambda: initialize_generator(),
        outputs=gr.Textbox(visible=False),
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

