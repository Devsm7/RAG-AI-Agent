"""
Speech-to-Text endpoint - handles voice input
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os

from twuaqirag.services.speech_to_text import stt
from twuaqirag.rag.answer import generate_response

router = APIRouter()


@router.post("/voice-chat")
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
        transcription = stt.transcribe_audio(temp_audio_path)
        
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
