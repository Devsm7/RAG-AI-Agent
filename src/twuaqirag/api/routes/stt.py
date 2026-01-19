"""
Speech-to-Text endpoint - handles voice input with TTS response
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import os
import base64

from twuaqirag.services.speech_to_text import get_stt_service, SpeechToTextService
from twuaqirag.services.text_to_speech import get_tts_service, TextToSpeechService

from twuaqirag.rag.orchestrator import generate_response

router = APIRouter()


@router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form("voice_session"),
):
    """
    Handle voice chat messages with TTS response
    
    Process:
    1. Transcribe user's voice input (STT)
    2. Detect language from transcription
    3. Generate text response from RAG
    4. Convert response to speech (TTS) in same language
    5. Return transcription, text response, and audio response
    """
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")

    temp_audio_path = None
    temp_tts_path = None
    
    try:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # Transcribe audio
        stt_service = get_stt_service()
        stt_result = stt_service.transcribe_file(temp_audio_path)
        transcription = stt_result.text
        detected_language = stt_result.detected_language

        # Clean up input audio temp file
        try:
            os.unlink(temp_audio_path)
            temp_audio_path = None
        except:
            pass

        if not transcription:
            raise HTTPException(
                status_code=422,
                detail="Could not transcribe audio"
            )

        # Generate text response
        response_text = await generate_response(transcription, session_id)

        # Get TTS service
        tts_service = get_tts_service()

        # Determine TTS language (match user's language)
        # Map Whisper language codes to our TTS language codes
        tts_language = "en"  # default
        if detected_language in ["ar", "arabic"]:
            tts_language = "ar"
        elif detected_language in ["en", "english"]:
            tts_language = "en"
        else:
            # Fallback: detect from transcription text
            tts_language = tts_service._detect_language(transcription)

        # Generate TTS audio response
        print(f"🔊 Generating TTS response in {tts_language}...")
        temp_tts_path, tts_result = tts_service.synthesize_to_temp_file(
            response_text,
            language=tts_language
        )
        print(f"✅ TTS audio generated: {temp_tts_path}")
        print(f"📊 Sample rate: {tts_result.sample_rate} Hz")

        # Read audio file and encode as base64 for easy transmission
        with open(temp_tts_path, 'rb') as f:
            audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        print(f"📦 Audio file size: {len(audio_data)} bytes")
        print(f"📝 Base64 length: {len(audio_base64)} characters")

        # Clean up TTS temp file
        try:
            os.unlink(temp_tts_path)
            temp_tts_path = None
        except:
            pass

        print(f"🎉 Returning response with audio_base64")
        return {
            "transcription": transcription,
            "response": response_text,
            "audio_base64": audio_base64,
            "detected_language": detected_language,
            "tts_language": tts_language,
            "sample_rate": tts_result.sample_rate,
            "session_id": session_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp files if they exist
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        if temp_tts_path and os.path.exists(temp_tts_path):
            try:
                os.unlink(temp_tts_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

