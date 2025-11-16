# Deployment Guide for Hugging Face Spaces

This guide will help you deploy the SQL Query Generator to Hugging Face Spaces.

## 📋 Prerequisites

1. A Hugging Face account ([sign up here](https://huggingface.co/join))
2. All project files ready
3. `example_dataset.parquet` file in the repository

## 🚀 Quick Deployment Steps

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the form:
   - **Space name**: `sql-query-generator` (or your choice)
   - **SDK**: Select **Gradio**
   - **Hardware**: 
     - For CPU: Select **CPU basic** (free)
     - For GPU: Select **T4 small** or **T4 medium** (requires payment/credits)
   - **Visibility**: Public or Private
4. Click **"Create Space"**

### Step 2: Upload Files

Upload all these files to your Space repository:

**Required Files:**
- ✅ `app.py` - Main Gradio application
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Project documentation
- ✅ `example_dataset.parquet` - Dataset file
- ✅ `sql_generator.py` - SQL generation logic
- ✅ `schema_analyzer.py` - Schema analyzer
- ✅ `safety_validator.py` - Safety validator
- ✅ `conversation_manager.py` - Conversation manager

**Optional Files:**
- `config.yaml` - Configuration file
- `Dockerfile` - Custom Docker configuration
- `.gitignore` - Git ignore rules

### Step 3: Configure Environment Variables (Optional)

In your Space settings → **Variables**, you can set:

- `DATASET_PATH`: Path to dataset (default: `example_dataset.parquet`)
- `MODEL_NAME`: Model name (default: `NousResearch/Nous-Hermes-llama-2-7b`)
- `USE_QUANTIZATION`: Enable quantization (default: `true`)
- `HF_TOKEN`: Your Hugging Face token (if needed)

### Step 4: Wait for Build

Hugging Face Spaces will automatically:
1. Install dependencies from `requirements.txt`
2. Build the application
3. Start the Gradio app

The build process may take 5-10 minutes, especially on first deployment.

### Step 5: Access Your App

Once built, your app will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## ⚙️ Hardware Recommendations

### CPU Deployment (Free)
- **Hardware**: CPU basic
- **Memory**: ~8GB RAM
- **Speed**: Slower (30-60 seconds per query)
- **Cost**: Free
- **Best for**: Testing, demos

### GPU Deployment (Paid)
- **Hardware**: T4 small or T4 medium
- **Memory**: 16GB+ RAM
- **Speed**: Faster (5-15 seconds per query)
- **Cost**: ~$0.60/hour for T4 small
- **Best for**: Production use

## 🔧 Troubleshooting

### Issue: Model fails to load

**Solution:**
- Check that you have enough memory
- Enable quantization: Set `USE_QUANTIZATION=true`
- Use CPU hardware if GPU is unavailable
- Check model name is correct

### Issue: Out of memory errors

**Solution:**
- Enable 8-bit quantization (default)
- Use CPU hardware instead of GPU
- Reduce `max_length` in `sql_generator.py`
- Upgrade to larger GPU instance

### Issue: Slow inference

**Solution:**
- Use GPU hardware instead of CPU
- Reduce `max_length` parameter
- Use a smaller model (if available)

### Issue: Build fails

**Solution:**
- Check `requirements.txt` syntax
- Verify all files are uploaded
- Check Space logs for specific errors
- Ensure Python version is compatible (3.10+)

## 📝 Important Notes

1. **First Load**: The first time the app loads, it will download the model (~14GB), which can take 10-20 minutes.

2. **Model Caching**: After first load, the model is cached and subsequent loads are faster.

3. **Memory Usage**: 
   - Without quantization: ~14GB RAM
   - With 8-bit quantization: ~7GB RAM

4. **Timeout**: CPU instances may timeout on long operations. Consider using GPU for better reliability.

5. **Cost**: GPU instances are paid. Monitor your usage in Space settings.

## 🔐 Security

- Never commit `.env` files with secrets
- Use Space secrets for sensitive tokens
- The app only generates SELECT queries (safe operations)
- Input validation prevents SQL injection

## 📊 Monitoring

Monitor your Space:
- **Logs**: View in Space → Logs tab
- **Metrics**: View in Space → Metrics tab
- **Usage**: View in Space → Settings → Usage

## 🆘 Support

If you encounter issues:
1. Check the Space logs
2. Review error messages
3. Verify all files are correct
4. Check Hugging Face Spaces documentation
5. Open an issue on the repository

## 🔗 Useful Links

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [Model Card](https://huggingface.co/NousResearch/Nous-Hermes-llama-2-7b)

