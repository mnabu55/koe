import time
import numpy as np
import structlog

from src.audio import AudioCapture
from src.vad import VAD
from src.stt import STT
from src.llm import LLMCleaner
from src.inserter import TextInserter
from src.config import Config

log = structlog.get_logger()


class Pipeline:
    def __init__(
        self,
        config: Config,
        audio: AudioCapture | None = None,
        vad: VAD | None = None,
        stt: STT | None = None,
        llm: LLMCleaner | None = None,
        inserter: TextInserter | None = None,
    ) -> None:
        self._config = config
        self._audio = audio or AudioCapture()
        self._vad = vad or VAD()
        self._stt = stt or STT(model=config.whisper_model)
        self._llm = llm if llm is not None else (
            LLMCleaner(model=config.ollama_model, prompt_path=config.prompt_path)
            if config.llm_cleanup_enabled else None
        )
        self._inserter = inserter or TextInserter()

    def start(self) -> None:
        self._audio.start()
        log.debug("pipeline_started")

    def stop(self) -> None:
        t0 = time.monotonic()
        audio = self._audio.stop()

        if len(audio) == 0:
            log.debug("pipeline_skipped_silent")
            return

        if not self._vad.has_voice(audio):
            log.debug("pipeline_skipped_no_voice")
            return

        audio = self._vad.trim(audio)

        t1 = time.monotonic()
        text = self._stt.transcribe(audio, language=self._config.whisper_language)
        log.debug("pipeline_stt_done", ms=int((time.monotonic() - t1) * 1000))

        if not text:
            log.debug("pipeline_skipped_empty_transcript")
            return

        if self._llm:
            t2 = time.monotonic()
            text = self._llm.clean(text)
            log.debug("pipeline_llm_done", ms=int((time.monotonic() - t2) * 1000))

        self._inserter.insert(text)
        log.debug("pipeline_done", total_ms=int((time.monotonic() - t0) * 1000))
