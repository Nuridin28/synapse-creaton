# SQL Query Generator - Hugging Face Spaces Deployment Guide

This guide explains how to deploy the SQL Query Generator to Hugging Face Spaces.

## 📦 Files Required for Deployment

1. **app.py** - Main Gradio application (entry point for Spaces)
2. **requirements.txt** - Python dependencies
3. **README.md** - Project documentation (shown on Spaces page)
4. **example_dataset.parquet** - Dataset file (must be included in repository)
5. **All Python modules**:
   - `sql_generator.py`
   - `schema_analyzer.py`
   - `safety_validator.py`
   - `conversation_manager.py`

## 🚀 Deployment Steps

### 1. Create a Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **SDK**: Gradio
   - **Space name**: Your choice (e.g., `sql-query-generator`)
   - **Visibility**: Public or Private
   - **Hardware**: CPU (or GPU if you have access)

### 2. Upload Files

Upload all required files to your Space repository:
- `app.py`
- `requirements.txt`
- `README.md`
- `example_dataset.parquet`
- `sql_generator.py`
- `schema_analyzer.py`
- `safety_validator.py`
- `conversation_manager.py`

### 3. Configure Environment Variables (Optional)

In your Space settings, you can set:
- `DATASET_PATH`: Path to dataset file (default: `example_dataset.parquet`)
- `MODEL_NAME`: Model name (default: `NousResearch/Nous-Hermes-llama-2-7b`)
- `USE_QUANTIZATION`: Enable 8-bit quantization (default: `true`)

### 4. Hardware Requirements

- **Minimum**: CPU with at least 8GB RAM
- **Recommended**: GPU (T4 or better) for faster inference
- **Model Size**: ~7B parameters (requires ~14GB RAM without quantization, ~7GB with 8-bit quantization)

### 5. Build and Deploy

Hugging Face Spaces will automatically:
1. Install dependencies from `requirements.txt`
2. Run `app.py` as the entry point
3. Make the app available at `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

## ⚙️ Configuration

### Hardware Settings

For GPU deployment:
1. Go to Space settings
2. Select "GPU" hardware
3. Choose T4 (small) or A10G (large) based on your needs

### Environment Variables

Set in Space settings → Variables:
- `HF_TOKEN`: Your Hugging Face token (if model requires authentication)
- `DATASET_PATH`: Custom dataset path
- `MODEL_NAME`: Custom model name

## 🔧 Troubleshooting

### Model Loading Issues

If the model fails to load:
- Check that you have enough memory (use quantization)
- Verify the model name is correct
- Check Hugging Face token if required

### Out of Memory Errors

- Enable 8-bit quantization: Set `USE_QUANTIZATION=true`
- Use a smaller model
- Upgrade to GPU with more memory

### Slow Inference

- Use GPU hardware instead of CPU
- Reduce `max_length` parameter in `sql_generator.py`
- Use a smaller model

## 📝 Notes

- The first load may take several minutes as the model downloads and loads
- 8-bit quantization is enabled by default to reduce memory usage
- The app automatically initializes the model on first load
- Conversation history is maintained during the session

## 🔗 Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [Model Card: Nous-Hermes-Llama2-7b](https://huggingface.co/NousResearch/Nous-Hermes-llama-2-7b)

