import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROMPT_PATH = str(Path(__file__).parent.parent / "prompts" / "cleanup_ja.md")


@dataclass
class Config:
    whisper_model: str = os.getenv("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
    whisper_language: str = os.getenv("WHISPER_LANGUAGE", "ja")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    llm_cleanup_enabled: bool = os.getenv("LLM_CLEANUP_ENABLED", "true").lower() == "true"
    hotkey: str = os.getenv("HOTKEY", "ctrl+space")
    prompt_path: str = os.getenv("PROMPT_PATH", DEFAULT_PROMPT_PATH)
