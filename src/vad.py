import numpy as np
import torch
import structlog

log = structlog.get_logger()

SAMPLE_RATE = 16000


class VAD:
    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold
        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            trust_repo=True,
        )
        self._model = model
        self._model.eval()
        self._get_speech_timestamps = utils[0]
        log.debug("vad_loaded")

    def has_voice(self, audio: np.ndarray) -> bool:
        if len(audio) == 0:
            return False
        self._model.reset_states()
        tensor = torch.from_numpy(audio).float()
        timestamps = self._get_speech_timestamps(
            tensor,
            self._model,
            sampling_rate=SAMPLE_RATE,
            threshold=self._threshold,
        )
        result = len(timestamps) > 0
        log.debug("vad_result", has_voice=result, segments=len(timestamps))
        return result

    def trim(self, audio: np.ndarray) -> np.ndarray:
        if len(audio) == 0:
            return audio
        self._model.reset_states()
        tensor = torch.from_numpy(audio).float()
        timestamps = self._get_speech_timestamps(
            tensor,
            self._model,
            sampling_rate=SAMPLE_RATE,
            threshold=self._threshold,
        )
        if not timestamps:
            return audio
        start = timestamps[0]["start"]
        end = timestamps[-1]["end"]
        return audio[start:end]
