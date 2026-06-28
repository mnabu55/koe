import numpy as np
import mlx_whisper
import structlog

log = structlog.get_logger()

DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


class STT:
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self._model = model
        log.debug("stt_initialized", model=model)

    def transcribe(self, audio: np.ndarray, language: str = "ja") -> str:
        if len(audio) == 0:
            return ""
        log.debug("stt_transcribing", samples=len(audio))
        try:
            result = mlx_whisper.transcribe(
                audio,
                path_or_hf_repo=self._model,
                language=language,
                task="transcribe",
            )
            text: str = result["text"].strip()
        except Exception as e:
            log.error("stt_transcription_failed", error=str(e))
            return ""
        if not text:
            log.debug("stt_result_empty")
        else:
            log.debug("stt_result", text=text[:80])
        return text
