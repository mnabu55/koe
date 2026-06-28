import pytest
from unittest.mock import patch, call, MagicMock
from src.inserter import TextInserter


def test_insert_empty_string_does_nothing():
    with patch("pyperclip.copy") as mock_copy, \
         patch("subprocess.run") as mock_run:
        TextInserter().insert("")
    mock_copy.assert_not_called()
    mock_run.assert_not_called()


def test_insert_copies_text_to_clipboard():
    with patch("pyperclip.paste", return_value="old"), \
         patch("pyperclip.copy") as mock_copy, \
         patch("subprocess.run"), \
         patch("time.sleep"):
        TextInserter().insert("hello")
    mock_copy.assert_any_call("hello")


def test_insert_pastes_via_applescript():
    with patch("pyperclip.paste", return_value=""), \
         patch("pyperclip.copy"), \
         patch("time.sleep"), \
         patch("subprocess.run") as mock_run:
        TextInserter().insert("test text")

    all_args = " ".join(str(c) for c in mock_run.call_args_list)
    assert "keystroke" in all_args


def test_insert_restores_clipboard_after_paste():
    original = "original clipboard content"
    with patch("pyperclip.paste", return_value=original), \
         patch("pyperclip.copy") as mock_copy, \
         patch("subprocess.run"), \
         patch("time.sleep"):
        TextInserter().insert("new text")

    assert mock_copy.call_args_list[-1] == call(original)


def test_insert_restores_clipboard_even_on_subprocess_error():
    original = "clipboard before error"
    with patch("pyperclip.paste", return_value=original), \
         patch("pyperclip.copy") as mock_copy, \
         patch("subprocess.run", side_effect=Exception("osascript failed")), \
         patch("time.sleep"):
        TextInserter().insert("text")

    assert mock_copy.call_args_list[-1] == call(original)
