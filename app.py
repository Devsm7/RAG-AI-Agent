"""
FastAPI Web Interface for Twuaiq RAG Assistant
Bilingual support (English/Arabic) with voice input using faster-whisper
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import tempfile
import os
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from vector import retriever
from speech_to_text import SpeechToText

# Initialize Speech-to-Text with faster-whisper
stt = SpeechToText(
    whisper_model="small",      # small is good balance of speed/accuracy
    device="cpu",               # use "cuda" if you have GPU
    compute_type="int8"         # int8 for CPU, float16 for GPU
)

# Initialize FastAPI app
app = FastAPI(
    title="Twuaiq RAG Assistant",
    description="Bilingual AI Assistant for Twuaiq Academy",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chat Model
model = ChatOllama(model='aya:8b')

# Define Prompt with History (Bilingual Support)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful bilingual assistant for Twuaiq Academy (أكاديمية طويق). 

Instructions:
- Detect the language of the user's question (English or Arabic)
- Respond in the SAME language as the question
- Answer simply and directly using only the provided context
- Do NOT repeat the question
- Do NOT mention any internal IDs (like place_id or bootcamp_id)
- If the answer is not in the context, state that you don't know

Important:
- If the context contains time in 24-hour format (e.g., 14:00), convert it to 12-hour format with AM/PM (e.g., 2:00 PM) for English or (2:00 مساءً) for Arabic

Context: {bootcamps}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# Create Chain
chain = prompt | model

# History Management (per session)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrap Chain with History
conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# Pydantic Models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ClearHistoryRequest(BaseModel):
    session_id: Optional[str] = "default_session"

# Helper Functions
def transcribe_audio(audio_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio using faster-whisper (local, fast)
    
    Args:
        audio_path: Path to audio file
        language: Optional language code ("ar", "en", or None for auto-detect)
    
    Returns:
        Transcribed text
    """
    try:
        # Use faster-whisper for local transcription
        transcription = stt.transcribe_audio(
            audio_path,
            language=language,  # None = auto-detect
            task="transcribe",
            vad_filter=True     # Voice Activity Detection for better accuracy
        )
        return transcription
    except Exception as e:
        return f"Error: {str(e)}"

def generate_response(message: str, session_id: str) -> str:
    """Generate response for a message"""
    try:
        # Retrieve context
        bootcamps = retriever.invoke(message)
        
        # Generate answer with history
        result = conversation_chain.invoke(
            {"bootcamps": bootcamps, "question": message},
            config={"configurable": {"session_id": session_id}}
        )
        
        return result.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding='utf-8')
    return """
    <html>
        <head><title>Twuaiq RAG Assistant</title></head>
        <body>
            <h1>Welcome to Twuaiq RAG Assistant</h1>
            <p>The interface is loading...</p>
            <p>If you see this message, please ensure the static files are properly set up.</p>
        </body>
    </html>
    """

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Handle text chat messages"""
    if not chat_message.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    response = generate_response(chat_message.message, chat_message.session_id)
    
    return ChatResponse(
        response=response,
        session_id=chat_message.session_id
    )

@app.post("/api/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: Optional[str] = "voice_session"
):
    """Handle voice chat messages"""
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    # Save uploaded audio to temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        # Transcribe audio
        transcription = transcribe_audio(temp_audio_path)
        
        # Clean up temp file
        os.unlink(temp_audio_path)
        
        if transcription.startswith("Error"):
            return JSONResponse(
                status_code=500,
                content={"error": transcription, "transcription": "", "response": ""}
            )
        
        # Generate response
        response = generate_response(transcription, session_id)
        
        return {
            "transcription": transcription,
            "response": response,
            "session_id": session_id
        }
    
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals():
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/api/clear-history")
async def clear_history(request: ClearHistoryRequest):
    """Clear conversation history for a session"""
    session_id = request.session_id
    if session_id in store:
        store[session_id] = ChatMessageHistory()
    
    return {"message": "History cleared", "session_id": session_id}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "llama3.2",
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
    }

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

if __name__ == "__main__":
    print("🚀 Starting Twuaiq RAG Assistant FastAPI Server...")
    print("🌐 The interface will be available at: http://localhost:8000")
    print("📱 API documentation at: http://localhost:8000/docs")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
