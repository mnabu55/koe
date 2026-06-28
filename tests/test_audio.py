import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from src.audio import AudioCapture


def test_stop_returns_empty_when_no_data():
    capture = AudioCapture()
    result = capture.stop()
    assert isinstance(result, np.ndarray)
    assert len(result) == 0
    assert result.dtype == np.float32


def test_callback_accumulates_data():
    capture = AudioCapture()
    chunk = np.ones((512, 1), dtype="float32")
    capture._callback(chunk, 512, None, None)
    result = capture.stop()
    assert len(result) == 512
    assert np.all(result == 1.0)


def test_stop_clears_buffer():
    capture = AudioCapture()
    chunk = np.ones((256, 1), dtype="float32")
    capture._callback(chunk, 256, None, None)
    capture.stop()
    result = capture.stop()
    assert len(result) == 0


def test_start_clears_previous_buffer():
    capture = AudioCapture()
    chunk = np.ones((256, 1), dtype="float32")
    capture._callback(chunk, 256, None, None)
    mock_stream = MagicMock()
    with patch("sounddevice.InputStream", return_value=mock_stream):
        capture.start()
    result = capture.stop()
    assert len(result) == 0


def test_multiple_chunks_concatenated():
    capture = AudioCapture()
    for i in range(3):
        chunk = np.full((100, 1), float(i), dtype="float32")
        capture._callback(chunk, 100, None, None)
    result = capture.stop()
    assert len(result) == 300
    assert result[0] == pytest.approx(0.0)
    assert result[100] == pytest.approx(1.0)
    assert result[200] == pytest.approx(2.0)
