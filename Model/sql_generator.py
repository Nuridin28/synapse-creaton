"""
Main SQL Query Generator using Nous-Hermes-Llama2-7b model (open source, fine-tuned for instruction following).
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional, Dict
import re
import os
from dotenv import load_dotenv

from schema_analyzer import SchemaAnalyzer
from safety_validator import SafetyValidator
from conversation_manager import ConversationManager

# Load environment variables from .env file (if it exists)
try:
    load_dotenv()
except Exception:
    # If .env file has issues, continue without it
    # Token can also be set via environment variable directly
    pass


class SQLQueryGenerator:
    """Main class for generating SQL queries from natural language."""
    
    def __init__(
        self,
        dataset_path: str,
        model_name: str = "NousResearch/Nous-Hermes-llama-2-7b",
        use_quantization: bool = True,
        device_map: str = "auto"
    ):
        """
        Initialize SQL Query Generator.
        
        Args:
            dataset_path: Path to the parquet dataset file
            model_name: Hugging Face model name or local path
            use_quantization: Whether to use 8-bit quantization for memory efficiency
            device_map: Device mapping strategy
        """
        self.dataset_path = dataset_path
        self.model_name = model_name
        
        # Initialize components
        print("Loading schema analyzer...")
        self.schema_analyzer = SchemaAnalyzer(dataset_path)
        self.schema_info = self.schema_analyzer.analyze()
        
        print("Initializing safety validator...")
        self.safety_validator = SafetyValidator()
        
        print("Initializing conversation manager...")
        self.conversation_manager = ConversationManager()
        
        # Initialize model
        print(f"Loading model: {model_name}...")
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model(use_quantization, device_map)
        
        print("SQL Query Generator initialized successfully!")
    
    def _load_model(self, use_quantization: bool, device_map: str):
        """Load the Nous-Hermes-Llama2-7b model and tokenizer."""
        try:
            # Get Hugging Face token from environment
            hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN") or os.getenv("HF_TOKEN")
            
            if not hf_token:
                print("Warning: No Hugging Face token found. Some models may require authentication.")
            else:
                print(f"Using Hugging Face token (length: {len(hf_token)})")
            
            # Prepare tokenizer kwargs
            tokenizer_kwargs = {"trust_remote_code": True}
            if hf_token:
                tokenizer_kwargs["token"] = hf_token
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                **tokenizer_kwargs
            )
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with optional quantization
            model_kwargs = {
                "trust_remote_code": True,
                "device_map": device_map,
                "dtype": torch.float16 if torch.cuda.is_available() else torch.float32  # Use dtype instead of deprecated torch_dtype
            }
            
            # Add token if available
            if hf_token:
                model_kwargs["token"] = hf_token
            
            # Track if we're using CPU mode
            using_cpu_mode = False
            
            # Try to load with quantization if requested and GPU is available
            if use_quantization and torch.cuda.is_available():
                try:
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_threshold=6.0,
                        llm_int8_enable_fp32_cpu_offload=True  # Enable CPU offloading for models that don't fit in GPU RAM
                    )
                    model_kwargs["quantization_config"] = quantization_config
                    # Use balanced device_map for CPU offloading
                    if device_map == "auto":
                        model_kwargs["device_map"] = "balanced"  # Better for CPU offloading
                    
                    print("Attempting to load model with 8-bit quantization...")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        **model_kwargs
                    )
                    print("Model loaded successfully with quantization!")
                except Exception as quant_error:
                    error_str = str(quant_error)
                    if "GPU RAM" in error_str or "quantized model" in error_str or "CPU or the disk" in error_str:
                        print("Warning: Quantization failed due to insufficient GPU RAM. Falling back to CPU mode...")
                        # Remove quantization config and retry on CPU
                        model_kwargs.pop("quantization_config", None)
                        model_kwargs["device_map"] = "cpu"
                        model_kwargs["dtype"] = torch.float32
                        using_cpu_mode = True
                        self.model = AutoModelForCausalLM.from_pretrained(
                            self.model_name,
                            **model_kwargs
                        )
                        print("Model loaded successfully on CPU (quantization disabled).")
                    else:
                        raise
            else:
                # No quantization - load normally
                if not torch.cuda.is_available() or device_map == "cpu":
                    using_cpu_mode = True
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    **model_kwargs
                )
            
            # Create pipeline
            # When using device_map (accelerate), don't specify device parameter
            # The model is already on the correct device(s) via device_map
            # Check if model was loaded with device_map (accelerate)
            model_has_device_map = hasattr(self.model, 'hf_device_map') or model_kwargs.get("device_map") not in [None, "cpu"]
            
            if model_has_device_map:
                # Don't specify device when using accelerate/device_map
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer
                )
            else:
                # Determine device for pipeline (0 for GPU, -1 for CPU)
                pipeline_device = -1 if using_cpu_mode else (0 if torch.cuda.is_available() else -1)
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=pipeline_device
                )
            
        except Exception as e:
            error_msg = str(e)
            # If quantization fails due to insufficient GPU RAM, suggest disabling it
            if "GPU RAM" in error_msg or "quantized model" in error_msg or "CPU or the disk" in error_msg:
                raise RuntimeError(
                    f"Error loading model: {error_msg}\n\n"
                    "Solution: Try disabling quantization by setting use_quantization=False:\n"
                    "  generator = SQLQueryGenerator(dataset_path='...', use_quantization=False)"
                )
            raise RuntimeError(f"Error loading model: {error_msg}")
    
    def _build_prompt(self, user_input: str, is_follow_up: bool = False) -> str:
        """
        Build the prompt for the model following the exact format from requirements.
        
        Args:
            user_input: User's natural language input
            is_follow_up: Whether this is a follow-up query
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # System instructions - exact format from requirements
        prompt_parts.append("You are an advanced SQL Query Generator fine-tuned for Nuraly's business transaction dataset.")
        prompt_parts.append("")
        prompt_parts.append("Your task: Convert natural language questions into **safe, correct, well-structured SQL SELECT queries only**.")
        prompt_parts.append("")
        prompt_parts.append("RULES YOU MUST FOLLOW:")
        prompt_parts.append("")
        prompt_parts.append("1. Always output ONLY SQL SELECT queries.")
        prompt_parts.append("2. NEVER generate DROP, DELETE, UPDATE, INSERT, ALTER, or TRUNCATE.")
        prompt_parts.append("3. Use only the exact column names and table names from the schema.")
        prompt_parts.append("4. Understand filtering conditions, numerical ranges, categories, amounts, OR/AND logic, date ranges, aggregates, grouping, sorting.")
        prompt_parts.append("   - For questions asking to count, calculate, or retrieve numbers, use COUNT(), SUM(), AVG(), etc. as appropriate.")
        prompt_parts.append("5. Always protect the database from harmful user input.")
        prompt_parts.append("6. If the user asks for something unsafe, politely refuse.")
        prompt_parts.append("7. Support conversation history:")
        prompt_parts.append("   - If the user says \"now show me…\" or references previous output,")
        prompt_parts.append("     continue from the previous SQL query.")
        prompt_parts.append("8. If the question is ambiguous, ask for clarification.")
        prompt_parts.append("9. Output no explanations — SQL ONLY.")
        prompt_parts.append("9a. CRITICAL: Generate ONLY ONE SQL query. Do NOT generate multiple queries, do NOT generate 'USER QUESTION:' or 'SQL QUERY:' markers after your answer. Stop immediately after the SQL query ends with a semicolon.")
        prompt_parts.append("10. CRITICAL - ENGLISH ONLY RULE: The entire SQL query MUST be in English, regardless of the language of the user's question.")
        prompt_parts.append("    - ALL SQL keywords must be in English: SELECT, FROM, WHERE, AND, OR, etc.")
        prompt_parts.append("    - ALL values in the query MUST be in English, exactly as they appear in the database.")
        prompt_parts.append("    - ALL column names must be in English (from the schema).")
        prompt_parts.append("    - ALL table names must be in English (from the schema).")
        prompt_parts.append("    - ALL string literals (city names, categories, etc.) MUST be in English.")
        prompt_parts.append("    - Example: If user asks 'Посчитай сколько в Алмате', use 'Almaty' (not 'Алматы' or 'Алмата').")
        prompt_parts.append("    - Example: If user asks 'в Астане', use 'Astana' (not 'Астана').")
        prompt_parts.append("    - Always check the EXAMPLE VALUES in the schema to see the exact English values used in the database.")
        prompt_parts.append("    - Translate ALL non-English values from the user's question to their English equivalents from the database.")
        prompt_parts.append("11. CRITICAL: Parse dates and years correctly from the user's question.")
        prompt_parts.append("    - If the user says 'ноябре 23 года' or 'November 23', this means November 2023 (year 2023).")
        prompt_parts.append("    - If the user says '2023', use year 2023, not 2020 or any other year.")
        prompt_parts.append("    - Always use the correct year from the user's question: '23 года' = 2023, '24 года' = 2024, etc.")
        prompt_parts.append("    - Date values in SQL must be in English format: '2023-11-01' (YYYY-MM-DD).")
        prompt_parts.append("")
        
        # Schema information
        prompt_parts.append("SCHEMA INFORMATION:")
        prompt_parts.append(self.schema_analyzer.get_schema_prompt())
        
        # Conversation context if follow-up
        if is_follow_up:
            context = self.conversation_manager.get_context_prompt()
            if context:
                prompt_parts.append("")
                prompt_parts.append("CONVERSATION CONTEXT:")
                prompt_parts.append(context)
                prompt_parts.append("")
                prompt_parts.append("The user is asking for a follow-up query. Generate SQL that continues from the previous query.")
        
        # User input
        prompt_parts.append("")
        prompt_parts.append("USER QUESTION:")
        prompt_parts.append(user_input)
        prompt_parts.append("")
        prompt_parts.append("SQL QUERY:")
        
        return "\n".join(prompt_parts)
    
    def _extract_sql(self, generated_text: str) -> str:
        """
        Extract SQL query from model output - SQL ONLY, no explanations.
        
        Args:
            generated_text: Raw text generated by the model
            
        Returns:
            Extracted SQL query (SQL ONLY)
        """
        # Handle None or empty input
        if not generated_text:
            return ""
        
        # Remove any leading/trailing whitespace
        text = str(generated_text).strip()
        
        if not text:
            return ""
        
        # CRITICAL: Stop at "USER QUESTION:" or "SQL QUERY:" markers to prevent model from generating new prompts
        # Find the first occurrence of these markers and cut text there
        user_question_pos = text.upper().find('USER QUESTION:')
        sql_query_pos = text.upper().find('SQL QUERY:')
        
        # Find the earliest position of these markers (but not at the start, as that's part of our prompt)
        cutoff_pos = len(text)
        if user_question_pos > 0:  # Only if not at position 0 (which would be our prompt)
            cutoff_pos = min(cutoff_pos, user_question_pos)
        if sql_query_pos > 0:  # Only if not at position 0
            cutoff_pos = min(cutoff_pos, sql_query_pos)
        
        # Cut text at the first marker to prevent taking subsequent generated prompts
        if cutoff_pos < len(text):
            text = text[:cutoff_pos].strip()
        
        # Look for SQL query after "SQL QUERY:" marker (in the original prompt format)
        sql_match = re.search(
            r'SQL QUERY:\s*(.*?)(?:\n\n|\n[A-Z]|USER QUESTION:|SQL QUERY:|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        if sql_match:
            sql = sql_match.group(1).strip()
        else:
            # If no marker found, try to find SELECT statement directly
            # More flexible pattern to catch SELECT statements, but stop at USER QUESTION or SQL QUERY
            select_match = re.search(
                r'(SELECT\s+.*?)(?:\n\n|\n(?:Please|Note|Explanation|This|The query|USER QUESTION|SQL QUERY)|USER QUESTION:|SQL QUERY:|$)',
                text,
                re.DOTALL | re.IGNORECASE
            )
            if select_match:
                sql = select_match.group(1).strip()
            else:
                # Try to find first SELECT statement with semicolon or end of text
                select_match = re.search(r'(SELECT.*?)(?:;|USER QUESTION:|SQL QUERY:|$|\n\n)', text, re.DOTALL | re.IGNORECASE)
                if select_match:
                    sql = select_match.group(1).strip()
                else:
                    # Last resort: if text contains SELECT, use everything up to first explanation or marker
                    if 'SELECT' in text.upper():
                        # Find SELECT and take everything until explanation pattern, USER QUESTION, or SQL QUERY
                        select_start = text.upper().find('SELECT')
                        sql = text[select_start:].strip()
                        # Remove everything after common explanation patterns or markers
                        for pattern in ['\n\nUSER QUESTION:', '\n\nSQL QUERY:', '\nUSER QUESTION:', '\nSQL QUERY:', 'USER QUESTION:', 'SQL QUERY:', '\n\n', '\nPlease', '\nNote', '\nExplanation']:
                            if pattern.upper() in sql.upper():
                                sql = sql.split(pattern)[0].strip() if pattern in sql else sql.split(pattern.upper())[0].strip()
                                break
                    else:
                        sql = text.strip()
        
        # Clean up the SQL - remove markdown code blocks and chat format tokens
        sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*', '', sql)
        # Remove LLaMA-2 chat format tokens that might appear in output
        sql = re.sub(r'\[/INST\]\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\[INST\]\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'<s>\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'</s>\s*', '', sql, flags=re.IGNORECASE)
        
        # Remove any explanatory text that might follow the SQL
        # Stop at common explanation patterns
        explanation_patterns = [
            r'(.*?)(?:Please|Note|Explanation|This query|The query|This will|This returns)',
            r'(.*?)(?:--.*$)',
        ]
        for pattern in explanation_patterns:
            match = re.search(pattern, sql, re.DOTALL | re.IGNORECASE)
            if match:
                sql = match.group(1).strip()
        
        # Extract only the SQL statement (stop at first non-SQL keyword that indicates explanation)
        sql_lines = []
        for line in sql.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # CRITICAL: Stop if we hit "USER QUESTION:" or "SQL QUERY:" markers (model is generating new prompts)
            if 'USER QUESTION:' in line.upper() or 'SQL QUERY:' in line.upper():
                break
            
            # Stop if we hit chat format tokens
            if '[/INST]' in line or '[INST]' in line:
                # Remove the token and everything after it
                line = re.sub(r'\[/INST\].*$', '', line, flags=re.IGNORECASE)
                if line.strip():
                    sql_lines.append(line.strip())
                break
            
            # Stop if we hit an explanation
            if re.match(r'^(Please|Note|Explanation|This|The query|This will|This returns)', line, re.IGNORECASE):
                break
            
            # Stop if we hit a comment that's not SQL-style
            if line.startswith('#') and not any(kw in line.upper() for kw in ['SELECT', 'FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'JOIN']):
                break
            
            sql_lines.append(line)
        
        sql = ' '.join(sql_lines).strip()
        
        # Remove any remaining "USER QUESTION:" or "SQL QUERY:" text that might have been included
        sql = re.sub(r'USER QUESTION:.*$', '', sql, flags=re.IGNORECASE | re.DOTALL)
        sql = re.sub(r'SQL QUERY:.*$', '', sql, flags=re.IGNORECASE | re.DOTALL)
        sql = sql.strip()
        
        # Ensure it ends properly
        if sql and not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def _is_sql_related_query(self, user_input: str) -> bool:
        """
        Check if the user input is related to SQL/database queries.
        
        Args:
            user_input: User's input text
            
        Returns:
            True if the query is SQL-related, False otherwise
        """
        input_lower = user_input.lower().strip()
        
        # Common greetings and non-SQL questions
        greetings = [
            'привет', 'hello', 'hi', 'hey', 'здравствуй', 'добрый',
            'как дела', 'how are you', 'как поживаешь', 'что нового',
            'спасибо', 'thanks', 'thank you', 'благодарю',
            'пока', 'bye', 'до свидания', 'goodbye',
            'как тебя зовут', 'what is your name', 'who are you',
            'что ты умеешь', 'what can you do', 'что ты делаешь',
            'помощь', 'help', 'помоги', 'help me'
        ]
        
        # Check for greetings
        for greeting in greetings:
            if greeting in input_lower:
                return False
        
        # SQL/database related keywords that indicate a real query
        sql_keywords = [
            'select', 'show', 'find', 'get', 'count', 'sum', 'avg', 'max', 'min',
            'where', 'from', 'table', 'database', 'query',
            'транзакц', 'transaction', 'данные', 'data', 'записи', 'records',
            'сколько', 'how many', 'count', 'посчитай', 'calculate',
            'покажи', 'show me', 'выведи', 'display', 'get',
            'найди', 'find', 'ищи', 'search', 'filter',
            'в', 'in', 'из', 'from', 'от', 'from',
            'дата', 'date', 'время', 'time', 'год', 'year', 'месяц', 'month',
            'город', 'city', 'сумма', 'amount', 'категория', 'category',
            'больше', 'more than', 'greater', 'меньше', 'less than',
            'между', 'between', 'и', 'and', 'или', 'or'
        ]
        
        # Check if input contains SQL-related keywords
        for keyword in sql_keywords:
            if keyword in input_lower:
                return True
        
        # If input is very short and doesn't contain SQL keywords, likely not a query
        if len(input_lower.split()) <= 3 and not any(kw in input_lower for kw in sql_keywords):
            return False
        
        # Default: assume it might be a query if it's not clearly a greeting
        return True
    
    def generate(
        self,
        user_input: str,
        max_length: int = 256,  # Reduced from 512 for faster generation
        temperature: float = 0.1,
        top_p: float = 0.95,
        return_explanation: bool = False
    ) -> str:
        """
        Generate SQL query from natural language input.
        
        Args:
            user_input: Natural language question
            max_length: Maximum length of generated text (reduced default for faster generation)
            temperature: Sampling temperature (lower = more deterministic) - not used with greedy decoding
            top_p: Nucleus sampling parameter - not used with greedy decoding
            return_explanation: Whether to return explanation (always False per requirements)
            
        Returns:
            Generated SQL query string
        """
        # Validate input is not empty
        if not user_input or not str(user_input).strip():
            return "-- ERROR: Empty query provided. Please enter a question."
        
        # Check if the query is SQL-related
        if not self._is_sql_related_query(user_input):
            return "-- This is not a SQL query request. Please ask questions about the database, such as:\n--   - 'Show me all transactions above $1000'\n--   - 'Count transactions in Almaty in November 2023'\n--   - 'Find transactions between dates'\n--   etc."
        
        # Sanitize input
        try:
            sanitized_input = self.safety_validator.sanitize_input(str(user_input).strip())
        except ValueError as e:
            # Per requirement: "If the user asks for something unsafe, politely refuse."
            return f"-- ERROR: {str(e)}"
        
        # Check if this is a follow-up query
        is_follow_up = self.conversation_manager.is_follow_up(sanitized_input)
        
        # Build prompt using LLaMA-2 chat format (Nous-Hermes is based on LLaMA-2)
        prompt = self._build_prompt(sanitized_input, is_follow_up)
        
        # Format for Nous-Hermes (uses LLaMA-2 chat format)
        formatted_prompt = self._format_llama2_prompt(prompt)
        
        # Generate SQL
        try:
            # Get model's max length from tokenizer or model config
            model_max_length = getattr(self.tokenizer, 'model_max_length', None)
            if model_max_length is None or model_max_length > 100000:  # Some tokenizers have very large defaults
                model_max_length = getattr(self.model.config, 'max_position_embeddings', 4096)
            
            # Use greedy decoding (do_sample=False) for faster and more deterministic generation
            # This avoids the temperature/top_p warning and is faster than sampling
            # Only use max_new_tokens to avoid the warning about both being set
            # Set truncation=False to avoid the warning (model will handle length limits naturally)
            outputs = self.pipeline(
                formatted_prompt,
                max_new_tokens=max_length,  # Maximum new tokens to generate
                do_sample=False,  # Greedy decoding for speed (faster than sampling)
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False,
                truncation=False,  # Disable truncation to avoid warning (model handles limits)
                use_cache=True  # Enable KV cache for faster generation
            )
            
            generated_text = outputs[0]['generated_text']
            print(f"Raw generated text: {generated_text[:500]}...")  # Log first 500 chars
            
            sql_query = self._extract_sql(generated_text)
            print(f"Extracted SQL: {sql_query}")
            
            # Check if extracted SQL is empty
            if not sql_query or not sql_query.strip():
                print(f"WARNING: Extracted SQL is empty. Raw text was: {generated_text}")
                # Try to return the raw text if extraction failed
                if generated_text.strip():
                    # If there's any text, try to find SELECT in it
                    if 'SELECT' in generated_text.upper():
                        # Return raw text as fallback
                        return generated_text.strip()
                    else:
                        return f"-- ERROR: Could not extract SQL query from model output. Model generated: {generated_text[:200]}"
                else:
                    return "-- ERROR: Model generated empty response. Please try again."
            
            # Check if model asked for clarification (ambiguous question)
            if any(phrase in generated_text.lower() for phrase in ['clarification', 'ambiguous', 'unclear', 'please specify']):
                # Return a comment indicating clarification is needed
                return "-- Please clarify your question. The request is ambiguous."
            
            # Validate the generated SQL
            is_valid, error_msg = self.safety_validator.validate(sql_query)
            
            if not is_valid:
                # Per requirement: "If the user asks for something unsafe, politely refuse."
                print(f"Validation failed: {error_msg}")
                return f"-- ERROR: {error_msg}"
            
            # Add to conversation history
            self.conversation_manager.add_turn(sanitized_input, sql_query)
            
            # Return SQL ONLY - no explanations
            return sql_query
            
        except Exception as e:
            return f"-- ERROR: Failed to generate SQL - {str(e)}"
    
    def _format_llama2_prompt(self, prompt: str) -> str:
        """
        Format prompt for Nous-Hermes-Llama2-7b model using chat template.
        Nous-Hermes is based on LLaMA-2, so it uses the same [INST] ... [/INST] format.
        
        Args:
            prompt: The prompt text
            
        Returns:
            Formatted prompt for Nous-Hermes
        """
        # Nous-Hermes (based on LLaMA-2) uses [INST] ... [/INST] format
        # Try to use the tokenizer's chat template if available
        system_msg = "You are an advanced SQL Query Generator. Output ONLY ONE SQL SELECT query in English, no explanations, no additional text. Stop immediately after the semicolon. Do NOT generate 'USER QUESTION:' or 'SQL QUERY:' markers. ALL SQL queries, values, column names, and string literals MUST be in English, regardless of the question language."
        
        if hasattr(self.tokenizer, 'apply_chat_template') and self.tokenizer.chat_template:
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except:
                # Fallback to LLaMA-2 format if chat template fails (Nous-Hermes uses LLaMA-2 format)
                return f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{prompt} [/INST]"
        else:
            # Fallback format for Nous-Hermes (LLaMA-2 based)
            return f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{prompt} [/INST]"
    
    def get_schema_info(self) -> Dict:
        """Get schema information."""
        return self.schema_info
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_manager.clear_history()

