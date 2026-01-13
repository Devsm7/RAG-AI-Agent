# 🚀 Setup Guide for New Users

This guide helps you set up the Twuaiq RAG Assistant after cloning the repository.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed ([Download here](https://ollama.ai))
3. **Git** installed

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Devsm7/RAG-AI-Agent.git
cd RAG-AI-Agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama Model

```bash
# Install the bilingual chat model
ollama pull aya:8b
```

### 5. Download HuggingFace Embeddings

The embeddings will be downloaded automatically on first run (~466 MB).
They will be cached in the `models/` folder.

### 6. Build Vector Database

```bash
# Run vector.py to build the ChromaDB database
python vector.py
```

This will:
- Load data from `datasets/bootcamps_db.csv` and `datasets/places_db.csv`
- Create embeddings using HuggingFace model
- Build the vector database in `chroma_db/` folder

### 7. Download Whisper Model

The faster-whisper model will be downloaded automatically on first run.
- Model: `small` (~466 MB)
- Cached locally for offline use

## 🚀 Running the Application

### Option 1: FastAPI Web Interface (Recommended)

```bash
# Using batch file (Windows)
start_fastapi.bat

# Or manually
python app.py
```

Then visit: **http://localhost:8000**

### Option 2: Command Line Interface

```bash
python main.py
```

## 📁 Expected Folder Structure After Setup

```
RAG-AI-Agent/
├── .venv/                    # Virtual environment (created)
├── models/                   # HuggingFace models (auto-downloaded)
├── chroma_db/                # Vector database (auto-created)
├── datasets/                 # CSV data files (included)
├── static/                   # Web interface files (included)
├── app.py                    # FastAPI backend
├── vector.py                 # Vector store setup
├── speech_to_text.py         # Speech-to-text module
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## ⚠️ Important Notes

### Large Files Not Included

The following folders are **NOT** in the repository (too large for GitHub):
- `models/` - HuggingFace embedding models (~466 MB)
- `chroma_db/` - Vector database (~350 KB)
- `.venv/` - Virtual environment

These will be created automatically when you run the application.

### First Run

The first time you run the application:
1. HuggingFace model will download (~466 MB) - takes 2-5 minutes
2. faster-whisper model will download (~466 MB) - takes 2-5 minutes
3. Vector database will be built from CSV files - takes ~10 seconds

Subsequent runs will be instant as everything is cached.

## 🔍 Verification

### Check Ollama Model
```bash
ollama list
# Should show: aya:8b
```

### Check Python Packages
```bash
pip list | findstr "fastapi langchain faster-whisper"
```

### Test the Application
```bash
python app.py
```

Visit http://localhost:8000 - you should see the web interface.

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Ollama model not found"
```bash
# Install the model
ollama pull aya:8b

# Verify it's installed
ollama list
```

### "Port 8000 already in use"
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Slow First Run
This is normal! The models are downloading:
- HuggingFace embeddings: ~466 MB
- faster-whisper: ~466 MB
- Total: ~1 GB download on first run

## 📚 Next Steps

After setup, check out:
- **README.md** - Full documentation
- **API_REFERENCE.md** - API endpoint details
- **FASTER_WHISPER_INTEGRATION.md** - Speech-to-text guide

## 🎯 Quick Test

```python
# Test the RAG system
python -c "from vector import retriever; print(retriever.invoke('What bootcamps are available?'))"
```

## 💡 Tips

1. **Use GPU**: If you have a GPU, edit `app.py` line 25:
   ```python
   device="cuda"  # Instead of "cpu"
   ```

2. **Smaller Model**: For faster startup, use tiny whisper model:
   ```python
   whisper_model="tiny"  # Instead of "small"
   ```

3. **Production**: Use multiple workers:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

**Need help? Check the full README.md or open an issue on GitHub!**
