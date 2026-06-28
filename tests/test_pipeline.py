import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from src.pipeline import Pipeline
from src.config import Config


@pytest.fixture
def config():
    return Config(llm_cleanup_enabled=False)


@pytest.fixture
def mock_components():
    audio = MagicMock()
    vad = MagicMock()
    stt = MagicMock()
    inserter = MagicMock()
    return audio, vad, stt, inserter


def test_pipeline_starts_audio_capture(config, mock_components):
    audio, vad, stt, inserter = mock_components
    pipeline = Pipeline(config=config, audio=audio, vad=vad, stt=stt, inserter=inserter)
    pipeline.start()
    audio.start.assert_called_once()


def test_pipeline_stop_skips_silent_audio(config, mock_components):
    audio, vad, stt, inserter = mock_components
    audio.stop.return_value = np.array([], dtype="float32")

    pipeline = Pipeline(config=config, audio=audio, vad=vad, stt=stt, inserter=inserter)
    pipeline.start()
    pipeline.stop()

    inserter.insert.assert_not_called()


def test_pipeline_stop_skips_no_voice(config, mock_components):
    audio, vad, stt, inserter = mock_components
    audio.stop.return_value = np.ones(16000, dtype="float32")
    vad.has_voice.return_value = False

    pipeline = Pipeline(config=config, audio=audio, vad=vad, stt=stt, inserter=inserter)
    pipeline.start()
    pipeline.stop()

    stt.transcribe.assert_not_called()
    inserter.insert.assert_not_called()


def test_pipeline_transcribes_and_inserts(config, mock_components):
    audio, vad, stt, inserter = mock_components
    audio.stop.return_value = np.ones(16000, dtype="float32")
    vad.has_voice.return_value = True
    vad.trim.return_value = np.ones(14000, dtype="float32")
    stt.transcribe.return_value = "テスト"

    pipeline = Pipeline(config=config, audio=audio, vad=vad, stt=stt, inserter=inserter)
    pipeline.start()
    pipeline.stop()

    stt.transcribe.assert_called_once()
    inserter.insert.assert_called_once_with("テスト")


def test_pipeline_with_llm_cleanup(mock_components):
    config = Config(llm_cleanup_enabled=True, ollama_model="test-model", prompt_path="/tmp/nonexistent")
    audio, vad, stt, inserter = mock_components
    audio.stop.return_value = np.ones(16000, dtype="float32")
    vad.has_voice.return_value = True
    vad.trim.return_value = np.ones(14000, dtype="float32")
    stt.transcribe.return_value = "えーとテスト"

    llm = MagicMock()
    llm.clean.return_value = "テスト"

    pipeline = Pipeline(config=config, audio=audio, vad=vad, stt=stt, llm=llm, inserter=inserter)
    pipeline.start()
    pipeline.stop()

    llm.clean.assert_called_once_with("えーとテスト")
    inserter.insert.assert_called_once_with("テスト")
