"""
Text-to-Speech API endpoint
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Literal
import base64

from twuaqirag.services.text_to_speech import get_tts_service

router = APIRouter()


class TTSRequest(BaseModel):
    """Request model for TTS"""
    text: str
    language: Literal["en", "ar", "auto"] = "auto"
    format: Literal["wav", "base64"] = "base64"


class TTSResponse(BaseModel):
    """Response model for TTS"""
    audio_base64: str
    language: str
    sample_rate: int
    audio_size: int


@router.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    
    Args:
        text: Text to convert to speech
        language: Language code ("en", "ar", or "auto" for detection)
        format: Output format ("wav" for audio file, "base64" for base64 encoded)
    
    Returns:
        Base64 encoded audio data with metadata
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        tts_service = get_tts_service()
        
        # Generate audio
        result = tts_service.synthesize_text(
            request.text,
            language=request.language
        )
        
        # Encode as base64
        audio_base64 = base64.b64encode(result.audio_data).decode('utf-8')
        
        return TTSResponse(
            audio_base64=audio_base64,
            language=result.language,
            sample_rate=result.sample_rate,
            audio_size=len(result.audio_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating speech: {str(e)}"
        )


@router.post("/text-to-speech/wav")
async def text_to_speech_wav(request: TTSRequest):
    """
    Convert text to speech and return WAV file
    
    Args:
        text: Text to convert to speech
        language: Language code ("en", "ar", or "auto" for detection)
    
    Returns:
        WAV audio file
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        tts_service = get_tts_service()
        
        # Generate audio
        result = tts_service.synthesize_text(
            request.text,
            language=request.language
        )
        
        # Return as WAV file
        return Response(
            content=result.audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=tts_output_{result.language}.wav"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating speech: {str(e)}"
        )
