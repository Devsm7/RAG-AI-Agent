"""
Speech-to-Text (STT) service using faster-whisper.
- FastAPI friendly
- Lazy-loaded model (doesn't load on import)
- Supports Arabic/English (auto-detect or forced)
- Safe temp-file handling (delete only temp we created)
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Optional, Literal, Tuple

from faster_whisper import WhisperModel


Device = Literal["cpu", "cuda", "auto"]
Task = Literal["transcribe", "translate"]


@dataclass
class STTConfig:
    model_name: str = "small"     # small is a good default for speed/quality
    device: Device = "cpu"
    compute_type: str = "int8"    # int8 for CPU; float16 for GPU
    beam_size: int = 5
    vad_filter: bool = True


@dataclass
class STTResult:
    text: str
    detected_language: str = "unknown"
    duration: Optional[float] = None  # if you want later


class SpeechToTextService:
    """
    Lazy STT service wrapper around faster-whisper WhisperModel.
    """

    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or STTConfig()
        self._model: Optional[WhisperModel] = None

    def _resolve_device(self) -> str:
        """
        Decide actual device string for faster-whisper.
        """
        if self.config.device == "auto":
            # Simple heuristic: if CUDA_VISIBLE_DEVICES is set and not empty -> try cuda
            # You can improve this check later with torch/cuda detection if needed.
            cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
            return "cuda" if cuda_visible not in ("", "-1") else "cpu"
        return self.config.device

    def load(self) -> None:
        """
        Load the whisper model once. Safe to call multiple times.
        """
        if self._model is not None:
            return

        device = self._resolve_device()
        self._model = WhisperModel(
            self.config.model_name,
            device=device,
            compute_type=self.config.compute_type,
        )

    def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,   # "ar", "en", or None(auto)
        task: Task = "transcribe",
        beam_size: Optional[int] = None,
        vad_filter: Optional[bool] = None,
    ) -> STTResult:
        """
        Transcribe an audio file path. Does NOT delete the file.
        """
        self.load()

        assert self._model is not None  # for type checker

        segments, info = self._model.transcribe(
            file_path,
            language=language,
            task=task,
            beam_size=beam_size if beam_size is not None else self.config.beam_size,
            vad_filter=vad_filter if vad_filter is not None else self.config.vad_filter,
        )

        parts = []
        for seg in segments:
            t = (seg.text or "").strip()
            if t:
                parts.append(t)

        text = " ".join(parts).strip()
        detected = getattr(info, "language", "unknown") or "unknown"

        return STTResult(text=text, detected_language=detected)

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        *,
        suffix: str = ".wav",
        language: Optional[str] = None,
        task: Task = "transcribe",
        beam_size: Optional[int] = None,
        vad_filter: Optional[bool] = None,
    ) -> STTResult:
        """
        Transcribe raw audio bytes by writing to a temp file.
        Deletes temp file safely.
        """
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            return self.transcribe_file(
                tmp_path,
                language=language,
                task=task,
                beam_size=beam_size,
                vad_filter=vad_filter,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass


# ---- Dependency-friendly singleton factory (FastAPI use) ----

_stt_singleton: Optional[SpeechToTextService] = None

def get_stt_service() -> SpeechToTextService:
    """
    Use this as a FastAPI dependency:
        stt = Depends(get_stt_service)
    """
    global _stt_singleton
    if _stt_singleton is None:
        # You can load config from env here if you want.
        _stt_singleton = SpeechToTextService(
            STTConfig(
                model_name=os.getenv("WHISPER_MODEL", "small"),
                device=os.getenv("WHISPER_DEVICE", "cpu"),        # cpu/cuda/auto
                compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
                beam_size=int(os.getenv("WHISPER_BEAM_SIZE", "5")),
                vad_filter=os.getenv("WHISPER_VAD_FILTER", "true").lower() == "true",
            )
        )
    return _stt_singleton
