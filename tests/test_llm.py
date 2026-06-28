import pytest
from unittest.mock import MagicMock, patch
from src.llm import LLMCleaner


@pytest.fixture
def prompt_file(tmp_path):
    p = tmp_path / "cleanup_ja.md"
    p.write_text("テスト用プロンプト\n", encoding="utf-8")
    return str(p)


def test_clean_returns_model_response(prompt_file):
    mock_response = MagicMock()
    mock_response.message.content = "整形されたテキスト"

    with patch("ollama.chat", return_value=mock_response):
        cleaner = LLMCleaner(prompt_path=prompt_file, model="test-model")
        result = cleaner.clean("えーとテスト")

    assert result == "整形されたテキスト"


def test_clean_falls_back_on_ollama_error(prompt_file):
    with patch("ollama.chat", side_effect=Exception("connection refused")):
        cleaner = LLMCleaner(prompt_path=prompt_file, model="test-model")
        result = cleaner.clean("フォールバックテキスト")

    assert result == "フォールバックテキスト"


def test_clean_skips_empty_input(prompt_file):
    with patch("ollama.chat") as mock_chat:
        cleaner = LLMCleaner(prompt_path=prompt_file, model="test-model")
        result = cleaner.clean("")

    mock_chat.assert_not_called()
    assert result == ""


def test_clean_skips_whitespace_only_input(prompt_file):
    with patch("ollama.chat") as mock_chat:
        cleaner = LLMCleaner(prompt_path=prompt_file, model="test-model")
        result = cleaner.clean("   ")

    mock_chat.assert_not_called()
    assert result == "   "


def test_prompt_includes_input_text(prompt_file):
    mock_response = MagicMock()
    mock_response.message.content = "output"

    with patch("ollama.chat") as mock_chat:
        mock_chat.return_value = mock_response
        cleaner = LLMCleaner(prompt_path=prompt_file, model="test-model")
        cleaner.clean("テスト入力テキスト")

    messages = mock_chat.call_args.kwargs["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "テスト入力テキスト" in user_msg["content"]
