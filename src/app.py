"""AquaVoice: On-device macOS voice dictation application."""
import queue
import threading
import rumps
import structlog

from src.config import Config
from src.pipeline import Pipeline
from src.hotkey import HotkeyManager

log = structlog.get_logger()

ICON_IDLE = "🎤"
ICON_RECORDING = "🔴"
ICON_PROCESSING = "⏳"


class AquaVoiceApp(rumps.App):
    def __init__(self, config: Config) -> None:
        super().__init__(ICON_IDLE, quit_button=None)
        self._config = config
        self._pipeline: Pipeline | None = None
        self._hotkey: HotkeyManager | None = None
        self._enabled = True
        self._title_queue: queue.Queue[str] = queue.Queue()

        self._llm_item = rumps.MenuItem(
            f"LLM: {'ON' if config.llm_cleanup_enabled else 'OFF'}"
        )
        self._hotkey_item = rumps.MenuItem(f"Hotkey: {config.hotkey}")
        self.menu = [
            self._llm_item,
            self._hotkey_item,
            None,
            rumps.MenuItem("Quit", callback=self._on_quit),
        ]

    @rumps.timer(0.05)
    def _flush_title(self, _: object) -> None:
        try:
            while True:
                self.title = self._title_queue.get_nowait()
        except queue.Empty:
            pass

    def _set_title(self, title: str) -> None:
        self._title_queue.put(title)

    def _on_quit(self, _: rumps.MenuItem | None = None) -> None:
        log.debug("app_quit")
        if self._hotkey:
            self._hotkey.stop()
        rumps.quit_application()

    def _initialize(self) -> None:
        try:
            self._pipeline = Pipeline(config=self._config)
            self._hotkey = HotkeyManager(
                on_press=self._on_hotkey_press,
                on_release=self._on_hotkey_release,
                hotkey=self._config.hotkey,
            )
            self._hotkey.start()
            log.debug("app_initialized")
        except Exception as e:
            log.error("app_init_failed", error=str(e))
            self._set_title("❌")

    def _on_hotkey_press(self) -> None:
        if not self._enabled or not self._pipeline:
            return
        self._set_title(ICON_RECORDING)
        self._pipeline.start()

    def _on_hotkey_release(self) -> None:
        if not self._enabled or not self._pipeline:
            return
        self._set_title(ICON_PROCESSING)
        try:
            self._pipeline.stop()
        finally:
            self._set_title(ICON_IDLE)

    def run(self) -> None:
        threading.Thread(target=self._initialize, daemon=True).start()
        super().run()


def main() -> None:
    config = Config()
    app = AquaVoiceApp(config=config)
    app.run()
