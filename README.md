# 🎓 Twuaiq RAG Assistant - FastAPI Edition

A modern, production-ready Retrieval-Augmented Generation (RAG) chatbot for Twuaiq Academy with FastAPI backend, beautiful web interface, and local speech-to-text capabilities.

## ✨ Features

### 🌐 **Web Interface**
- **Modern UI**: Beautiful, responsive web interface with gradient design
- **Bilingual Support**: Full English/Arabic support with automatic language detection
- **Text Chat**: Type your questions with real-time responses
- **Voice Chat**: Browser-based voice recording with local transcription
- **Session Management**: Separate conversation histories for text and voice
- **Mobile Friendly**: Fully responsive design

### 🚀 **FastAPI Backend**
- **REST API**: Professional API endpoints with auto-generated documentation
- **Fast Performance**: Async operations for better concurrency
- **Auto Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **CORS Enabled**: Ready for frontend integration
- **Health Checks**: Monitor system status

### 🧠 **AI Capabilities**
- **Local Embeddings**: HuggingFace multilingual embeddings (offline)
- **Fast Transcription**: faster-whisper for local speech-to-text (2-5 seconds)
- **Vector Search**: ChromaDB for efficient semantic search
- **Context-Aware**: Maintains conversation history
- **Bilingual RAG**: Optimized for English and Arabic queries

## 📋 Prerequisites

1. **Python 3.8+** with virtual environment
2. **Ollama** installed with models:
   - `aya:8b` (bilingual chat model)
   - ~~`mxbai-embed-large`~~ (replaced with HuggingFace)
   - ~~`karanchopda333/whisper`~~ (replaced with faster-whisper)

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd c:\Users\user\Desktop\RAG

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama Model

```bash
# Only need the chat model now
ollama pull aya:8b
```

### 3. Start the Server

**Option 1: Using batch file (easiest)**
```bash
start_fastapi.bat
```

**Option 2: Manual start**
```bash
python app.py
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 📡 API Endpoints

### 1. **Text Chat** - `/api/chat`

**Request** (JSON):
```json
{
  "message": "What bootcamps are available?",
  "session_id": "my_session"  // optional
}
```

**Response** (JSON):
```json
{
  "response": "The available bootcamps are...",
  "session_id": "my_session"
}
```

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What bootcamps are available?"}'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "What bootcamps are available?"}
)
print(response.json())
```

### 2. **Voice Chat** - `/api/voice-chat`

**Request** (multipart/form-data):
- `audio`: Audio file (WAV format)
- `session_id`: String (optional, default: "voice_session")

**Response** (JSON):
```json
{
  "transcription": "What bootcamps are available?",
  "response": "The available bootcamps are...",
  "session_id": "voice_session"
}
```

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/voice-chat" \
  -F "audio=@recording.wav" \
  -F "session_id=my_voice_session"
```

**Example (Python)**:
```python
import requests

with open("recording.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/api/voice-chat",
        files={"audio": audio_file},
        data={"session_id": "my_session"}
    )
print(response.json())
```

### 3. **Clear History** - `/api/clear-history`

**Request** (JSON):
```json
{
  "session_id": "my_session"  // optional
}
```

**Response** (JSON):
```json
{
  "message": "History cleared",
  "session_id": "my_session"
}
```

### 4. **Health Check** - `/api/health`

**Request**: GET (no body)

**Response** (JSON):
```json
{
  "status": "healthy",
  "model": "aya:8b",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

## 📁 Project Structure

```
RAG/
├── app.py                              # FastAPI backend with REST API
├── vector.py                           # Vector store (HuggingFace embeddings)
├── speech_to_text.py                   # faster-whisper transcription
├── requirements.txt                    # Python dependencies
├── start_fastapi.bat                   # Quick start script
├── static/                             # Web interface
│   ├── index.html                      # Main HTML page
│   ├── styles.css                      # Styling
│   └── app.js                          # JavaScript logic
├── datasets/
│   ├── bootcamps_db.csv               # Bootcamp data
│   └── places_db.csv                  # Places data
├── chroma_db/                         # Vector database
├── models/                            # HuggingFace model cache
├── FASTER_WHISPER_INTEGRATION.md     # Speech-to-text docs
└── .venv/                             # Virtual environment
```

## 🔧 How It Works

### Text Chat Flow:
```
User types question → FastAPI → Vector search → RAG → LLM → Response
```

### Voice Chat Flow:
```
Browser records audio → Upload to FastAPI → faster-whisper (local, 2-5s) 
→ Transcription → Vector search → RAG → LLM → Response
```

### Key Components:

1. **Embeddings**: HuggingFace `paraphrase-multilingual-MiniLM-L12-v2`
   - 384 dimensions
   - 50+ languages including Arabic
   - Cached locally in `models/`

2. **Speech-to-Text**: faster-whisper `small` model
   - Local transcription (no internet needed)
   - 2-5 second processing time
   - Automatic language detection
   - Voice Activity Detection (VAD)

3. **Chat Model**: Ollama `aya:8b`
   - Bilingual (English/Arabic)
   - Context-aware responses
   - Conversation history

4. **Vector Store**: ChromaDB
   - Semantic search
   - Top-10 retrieval
   - Persistent storage

## 🎨 Web Interface Features

### Text Chat Tab
- Type questions in English or Arabic
- Example questions for quick start
- Real-time responses
- Message history
- Clear conversation button

### Voice Chat Tab
- Browser-based recording (no installation)
- Visual recording indicator
- Automatic transcription
- Same RAG capabilities as text
- Separate session management

## ⚙️ Configuration

### Change Whisper Model Size

Edit `app.py` line 23-28:

```python
stt = SpeechToText(
    whisper_model="small",  # tiny/base/small/medium/large-v3
    device="cpu",           # "cuda" for GPU
    compute_type="int8"     # "float16" for GPU
)
```

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 75 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ |
| base | 145 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ |
| **small** | 466 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ (recommended) |
| medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| large-v3 | 3 GB | ⚡ | ⭐⭐⭐⭐⭐ |

### Change Server Port

Edit `app.py` line 250:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,  # Change this
    log_level="info"
)
```

### Customize UI

- **Colors**: Edit `static/styles.css` (lines 2-20 for CSS variables)
- **Layout**: Edit `static/index.html`
- **Functionality**: Edit `static/app.js`

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### Voice Recording Not Working
- Use Chrome or Edge browser
- Grant microphone permissions
- Ensure you're on localhost or HTTPS

### Ollama Not Responding
```bash
# Start Ollama service
ollama serve

# Verify model is available
ollama list
```

### Slow Transcription
- Try smaller whisper model (base or tiny)
- Use GPU if available (set device="cuda")
- Check CPU usage

## 📦 Dependencies

```
langchain                    # LangChain framework
langchain-ollama            # Ollama integration
langchain-chroma            # ChromaDB vector store
langchain-community         # Community integrations
langchain-huggingface       # HuggingFace embeddings
sentence-transformers       # Embedding models
faster-whisper              # Local speech-to-text
fastapi                     # Web framework
uvicorn[standard]           # ASGI server
python-multipart            # File upload support
pandas                      # Data processing
sounddevice                 # Audio recording (for testing)
soundfile                   # Audio file handling
numpy                       # Numerical operations
```

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (when server is running)
- **faster-whisper Integration**: See `FASTER_WHISPER_INTEGRATION.md`
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/

## 🚀 Production Deployment

### Using Multiple Workers
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### With HTTPS
```bash
uvicorn app:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Docker Deployment
```bash
docker-compose up -d
```

## 📝 Notes

- **First run**: Vector database and whisper model will be downloaded
- **Offline capable**: Works without internet after initial setup
- **Session management**: Each tab has separate conversation history
- **Auto cleanup**: Temporary audio files are automatically deleted
- **Bilingual**: Automatically detects and responds in the same language

## 🎯 Example Queries

### English
- "What bootcamps are available?"
- "Where is the cafeteria?"
- "What time does the Unity bootcamp start?"
- "Tell me about the Cyber Security bootcamp"

### Arabic
- "ما هي المعسكرات المتاحة؟"
- "أين تقع الكافتيريا؟"
- "متى يبدأ معسكر يونيتي؟"
- "أخبرني عن معسكر الأمن السيبراني"

## 📄 License

This project is for educational purposes at Twuaiq Academy.

---

**Built with ❤️ using FastAPI, LangChain, HuggingFace, and faster-whisper**
