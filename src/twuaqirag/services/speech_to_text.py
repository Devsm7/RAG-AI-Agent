"""
Speech-to-Text module using faster-whisper (local, fast transcription)
Optimized for FastAPI integration with bilingual support (English/Arabic)
"""
import os
import tempfile
from typing import Optional, Literal

from faster_whisper import WhisperModel


class SpeechToText:
    """
    Local speech-to-text transcription using faster-whisper.
    No Ollama required - runs completely offline after model download.
    """

    def __init__(
        self,
        whisper_model: str = "medium",
        device: Literal["cpu", "cuda", "auto"] = "cpu",
        compute_type: str = "int8",
        sample_rate: int = 16000,
    ):
        """
        Initialize Speech-to-Text with faster-whisper.
        
        Args:
            whisper_model: Model size (tiny/base/small/medium/large-v3)
                          - tiny: fastest, least accurate (~75MB)
                          - base: fast, decent accuracy (~145MB)
                          - small: balanced (recommended) (~466MB)
                          - medium: slower, better accuracy (~1.5GB)
                          - large-v3: best quality, slowest (~3GB)
            device: "cpu", "cuda", or "auto"
            compute_type: "int8" for CPU, "float16" for GPU
            sample_rate: Audio sample rate (16kHz optimal for Whisper)
        """
        self.sample_rate = sample_rate
        
        # Initialize whisper model once (important for performance)
        print(f"🔄 Loading faster-whisper model '{whisper_model}'...")
        self.whisper = WhisperModel(
            whisper_model,
            device=("cuda" if device == "auto" else device),
            compute_type=compute_type,
        )
        print(f"✅ Model loaded successfully!")

    def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        task: Literal["transcribe", "translate"] = "transcribe",
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> str:
        """
        Transcribe audio file using faster-whisper.
        
        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)
            language: Language code ("ar", "en", or None for auto-detect)
            task: "transcribe" (keep original language) or "translate" (to English)
            beam_size: Beam search size (higher = better quality, slower)
            vad_filter: Voice Activity Detection (removes silence)
        
        Returns:
            Transcribed text as string
        """
        try:
            print("🔄 Transcribing audio with faster-whisper...")

            # Transcribe using faster-whisper
            segments, info = self.whisper.transcribe(
                audio_file_path,
                language=language,
                task=task,
                beam_size=beam_size,
                vad_filter=vad_filter,
            )

            # Collect all segments
            text_parts = []
            for seg in segments:
                text = (seg.text or "").strip()
                if text:
                    text_parts.append(text)

            transcript = " ".join(text_parts).strip()

            # Log results
            detected_lang = getattr(info, 'language', 'unknown')
            print(f"✅ Detected language: {detected_lang}")
            print(f"✅ Transcript: {transcript[:100]}..." if len(transcript) > 100 else f"✅ Transcript: {transcript}")

            return transcript

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""
        finally:
            # Clean up temp file
            if os.path.exists(audio_file_path):
                try:
                    os.remove(audio_file_path)
                except:
                    pass  # Ignore cleanup errors


# Initialize global STT instance
stt = SpeechToText(
    whisper_model="medium",
    device="cpu",
    compute_type="int8"
)


# Test function (optional)
def test():
    """Test the speech-to-text module"""
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    
    print("🎤 Testing faster-whisper speech-to-text...")
    print("Recording 5 seconds of audio...")
    
    # Record audio
    sample_rate = 16000
    duration = 5
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("✅ Recording finished!")
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    sf.write(temp_file.name, audio_data, sample_rate)
    
    # Transcribe
    test_stt = SpeechToText(whisper_model="small", device="cpu", compute_type="int8")
    text = test_stt.transcribe_audio(temp_file.name, language=None)  # Auto-detect
    
    print(f"\n📝 Final transcription: {text}")


if __name__ == "__main__":
    test()
