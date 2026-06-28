import threading
from typing import Callable
from pynput import keyboard
import structlog

log = structlog.get_logger()


class HotkeyManager:
    def __init__(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        hotkey: str = "ctrl+space",
    ) -> None:
        self._on_press = on_press
        self._on_release = on_release
        self._hotkey = hotkey
        self._held = False
        self._held_lock = threading.Lock()
        self._listener: keyboard.Listener | None = None
        log.debug("hotkey_manager_initialized", hotkey=hotkey)

    def start(self) -> None:
        keys = self._parse_hotkey(self._hotkey)
        self._listener = keyboard.Listener(
            on_press=self._make_press_handler(keys),
            on_release=self._make_release_handler(keys),
        )
        self._listener.start()
        log.debug("hotkey_manager_started")

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        log.debug("hotkey_manager_stopped")

    def _parse_hotkey(self, hotkey: str) -> set[str]:
        return set(hotkey.lower().split("+"))

    def _make_press_handler(self, keys: set[str]) -> Callable:
        pressed: set[str] = set()

        def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            pressed.add(self._key_name(key))
            if keys <= pressed:
                with self._held_lock:
                    if not self._held:
                        self._held = True
                        log.debug("hotkey_pressed")
                        threading.Thread(
                            target=self._on_press, daemon=True
                        ).start()

        return on_press

    def _make_release_handler(self, keys: set[str]) -> Callable:
        pressed: set[str] = set()

        def on_release(key: keyboard.Key | keyboard.KeyCode) -> None:
            pressed.discard(self._key_name(key))
            with self._held_lock:
                if self._held and not keys <= pressed:
                    self._held = False
                    log.debug("hotkey_released")
                    threading.Thread(
                        target=self._on_release, daemon=True
                    ).start()

        return on_release

    def _key_name(self, key: keyboard.Key | keyboard.KeyCode) -> str:
        if isinstance(key, keyboard.KeyCode):
            return key.char.lower() if key.char else ""
        name = key.name.lower()
        aliases = {"ctrl_l": "ctrl", "ctrl_r": "ctrl", "space": "space"}
        return aliases.get(name, name)
