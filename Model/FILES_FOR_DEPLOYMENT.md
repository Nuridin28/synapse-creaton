# Files Required for Hugging Face Spaces Deployment

This document lists all files needed to deploy the SQL Query Generator to Hugging Face Spaces.

## ✅ Required Files (Must Upload)

### Core Application Files
1. **app.py** - Main Gradio application (entry point for Spaces)
2. **sql_generator.py** - SQL generation logic
3. **schema_analyzer.py** - Schema analysis from parquet files
4. **safety_validator.py** - SQL query validation and input sanitization
5. **conversation_manager.py** - Conversation history management

### Configuration Files
6. **requirements.txt** - Python dependencies (must include gradio)
7. **README.md** - Project documentation (shown on Spaces page)

### Data Files
8. **example_dataset.parquet** - Dataset file (must be included in repository)

## 📄 Optional Files (Recommended)

9. **config.yaml** - Hugging Face Spaces configuration
10. **Dockerfile** - Custom Docker configuration (optional)
11. **.gitignore** - Git ignore rules
12. **DEPLOYMENT.md** - Deployment guide
13. **README_HF.md** - Additional documentation

## 📋 File Checklist

Before deploying, verify you have:

- [ ] `app.py`
- [ ] `sql_generator.py`
- [ ] `schema_analyzer.py`
- [ ] `safety_validator.py`
- [ ] `conversation_manager.py`
- [ ] `requirements.txt` (with gradio>=4.0.0)
- [ ] `README.md`
- [ ] `example_dataset.parquet`
- [ ] `config.yaml` (optional)
- [ ] `.gitignore` (optional)

## 🚀 Quick Upload Instructions

1. Go to your Hugging Face Space
2. Click "Files and versions" tab
3. Click "Add file" → "Upload files"
4. Select all required files
5. Commit changes
6. Wait for automatic build

## ⚠️ Important Notes

- **File Size**: `example_dataset.parquet` should be uploaded directly (not via Git LFS unless very large)
- **Model**: The model will be downloaded automatically on first run (~14GB)
- **Memory**: Ensure your Space has enough memory (8GB+ recommended)
- **Dependencies**: All dependencies in `requirements.txt` will be installed automatically

## 📦 File Structure

```
your-space/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── config.yaml              # Configuration (optional)
├── sql_generator.py         # Core logic
├── schema_analyzer.py       # Schema analysis
├── safety_validator.py      # Validation
├── conversation_manager.py  # History management
└── example_dataset.parquet  # Dataset
```

## 🔍 Verification

After uploading, check:
1. All files are present in the repository
2. `requirements.txt` includes `gradio>=4.0.0`
3. `app.py` is the main entry point
4. `example_dataset.parquet` is accessible
5. Build logs show no errors

## 🆘 Troubleshooting

If files are missing:
- Check file names (case-sensitive)
- Verify file paths are correct
- Ensure all Python files are in root directory
- Check that `example_dataset.parquet` is uploaded

