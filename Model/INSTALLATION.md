# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) CUDA-capable GPU for faster inference (NVIDIA GPU recommended)
- Internet connection (to download the Nous-Hermes-Llama2-7b model on first run)

## Step 1: Install Python Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install torch>=2.0.0
pip install transformers>=4.35.0
pip install accelerate>=0.24.0
pip install bitsandbytes>=0.41.0
pip install pandas>=2.0.0
pip install pyarrow>=12.0.0
pip install fastparquet>=2023.10.0
pip install sqlparse>=0.4.4
pip install python-dotenv>=1.0.0
```

## Step 2: Verify Installation

Test that everything is installed correctly:

```bash
python -c "import torch; import transformers; import pandas; print('All packages installed successfully!')"
```

## Step 3: Prepare Your Dataset

Ensure `example_dataset.parquet` is in the project root directory.

## About Nous-Hermes-Llama2-7b (Open Source)

**Good news!** Nous-Hermes-Llama2-7b is fully open source and freely available. You don't need:
- ❌ Special access requests
- ❌ Hugging Face tokens
- ❌ Model approval

Nous-Hermes-Llama2-7b is a fine-tuned version of LLaMA-2, specifically optimized for instruction following tasks. This makes it excellent for SQL generation. The model will be automatically downloaded from Hugging Face on first use. Just make sure you have an internet connection.

## GPU vs CPU

- **GPU (Recommended)**: Much faster inference. Requires CUDA-capable NVIDIA GPU.
  - PyTorch will automatically detect and use CUDA if available
  - 8-bit quantization is enabled by default to reduce memory usage

- **CPU**: Works but will be slower. No additional setup needed.

## Troubleshooting

### Issue: "Unable to find a usable engine" for parquet files
**Solution**: Make sure pyarrow is installed:
```bash
pip install pyarrow --upgrade
```

### Issue: "CUDA out of memory"
**Solution**: The code uses 8-bit quantization by default. If you still run out of memory:
- The default model `NousResearch/Nous-Hermes-llama-2-7b` is already the 7B version (good balance)
- Reduce batch size
- Use CPU instead (set `use_quantization=False`)

### Issue: "bitsandbytes" errors on Windows
**Solution**: bitsandbytes may not work on Windows. You can disable quantization:
```python
generator = SQLQueryGenerator(
    dataset_path="example_dataset.parquet",
    use_quantization=False  # Disable quantization on Windows
)
```

### Issue: Slow model download
**Solution**: The Nous-Hermes-Llama2-7b model is about 13GB. On first run, it will download automatically. This is a one-time download. Subsequent runs will use the cached model.

### Issue: Model download fails
**Solution**: 
- Check your internet connection
- Ensure you have enough disk space (~15GB free)
- Try running again (downloads are resumable)

## Quick Start

Once installed, run:

```bash
python main.py
```

Or use the Python API:

```python
from sql_generator import SQLQueryGenerator

generator = SQLQueryGenerator("example_dataset.parquet")
sql = generator.generate("Show me all transactions above $1000")
print(sql)
```

## Model Options

The default model is **Nous-Hermes-Llama2-7b**, which is:
- Fine-tuned specifically for instruction following
- Excellent for SQL generation tasks
- Open source and freely available
- Good balance of performance and speed

You can also use other Nous-Hermes variants or LLaMA-2 models:

- **13B Nous-Hermes**: `NousResearch/Nous-Hermes-Llama2-13b` - Better performance, requires more memory
- **LLaMA-2 7B Chat**: `meta-llama/Llama-2-7b-chat-hf` - Base LLaMA-2 chat model
- **LLaMA-2 13B Chat**: `meta-llama/Llama-2-13b-chat-hf` - Larger LLaMA-2 chat model

To use a different model:

```python
generator = SQLQueryGenerator(
    dataset_path="example_dataset.parquet",
    model_name="NousResearch/Nous-Hermes-Llama2-13b"  # Use 13B Nous-Hermes model
)
```

## First Run

On the first run, the system will:
1. Download the Nous-Hermes-Llama2-7b model (~13GB)
2. Cache it locally for future use
3. Load the model into memory

This may take 10-30 minutes depending on your internet connection. Subsequent runs will be much faster as the model is cached locally.
