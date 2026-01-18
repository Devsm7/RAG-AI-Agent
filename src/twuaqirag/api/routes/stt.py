"""
Speech-to-Text endpoint - handles voice input
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import tempfile
import os

from twuaqirag.services.speech_to_text import get_stt_service, SpeechToTextService

from twuaqirag.rag.orchestrator import generate_response

router = APIRouter()


@router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form("voice_session"),
):
    """Handle voice chat messages"""
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")

    try:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # Transcribe audio
        stt_service = get_stt_service()
        result = stt_service.transcribe_file(temp_audio_path)
        transcription = result.text

        # Clean up temp file
        try:
            os.unlink(temp_audio_path)
        except:
            pass

        if not transcription:
            raise HTTPException(
                status_code=422,
                detail="Could not transcribe audio"
            )

        # Generate response
        response_text = await generate_response(transcription, session_id)

        return {
            "transcription": transcription,
            "response": response_text,
            "session_id": session_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals():
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
