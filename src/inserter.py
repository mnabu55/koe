import subprocess
import time
import pyperclip
import structlog

log = structlog.get_logger()

PASTE_DELAY = 0.05
RESTORE_DELAY = 0.1


class TextInserter:
    def insert(self, text: str) -> None:
        if not text:
            return
        original = pyperclip.paste()
        try:
            pyperclip.copy(text)
            time.sleep(PASTE_DELAY)
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "v" using command down',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            log.debug("text_inserted", length=len(text))
        except subprocess.CalledProcessError as e:
            log.error("insert_failed", return_code=e.returncode, stderr=e.stderr)
        except Exception as e:
            log.error("insert_failed", error=str(e))
        finally:
            time.sleep(RESTORE_DELAY)
            pyperclip.copy(original)
