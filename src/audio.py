import threading
import numpy as np
import sounddevice as sd
import structlog

log = structlog.get_logger()

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"


class AudioCapture:
    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self._sample_rate = sample_rate
        self._buffer: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            self._buffer.clear()
        self._stream = sd.InputStream(
            samplerate=self._sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
        self._stream.start()
        log.debug("audio_capture_started")

    def stop(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._buffer:
                return np.array([], dtype=DTYPE)
            audio = np.concatenate(self._buffer, axis=0).flatten()
            self._buffer.clear()
        log.debug("audio_capture_stopped", samples=len(audio))
        return audio

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: object,
        status: object,
    ) -> None:
        if status:
            log.warning("audio_callback_status", status=str(status))
        with self._lock:
            self._buffer.append(indata.copy())
