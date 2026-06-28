import ollama
import structlog
from pathlib import Path

log = structlog.get_logger()

DEFAULT_PROMPT_PATH = str(Path(__file__).parent.parent / "prompts" / "cleanup_ja.md")
DEFAULT_MODEL = "qwen2.5:7b"


class LLMCleaner:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        prompt_path: str = DEFAULT_PROMPT_PATH,
    ) -> None:
        self._model = model
        self._system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        log.debug("llm_initialized", model=model)

    def clean(self, text: str) -> str:
        if not text.strip():
            return text
        try:
            response = ollama.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": text},
                ],
            )
            result: str = response.message.content.strip()
            log.debug("llm_cleaned", original=text[:50], result=result[:50])
            return result
        except Exception as e:
            log.warning("llm_fallback", error=str(e))
            return text
