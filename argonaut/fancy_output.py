import sys
import os
from typing import Dict


class ProgressBar:
    def __init__(self, total: int, description: str = "Processing", width: int = 10):
        self.total = total
        self.description = description
        self.width = width

    def update(self, current: int) -> None:
        percent = current / self.total
        filled_length = int(self.width * percent)
        bar = "#" * filled_length + "-" * (self.width - filled_length)
        print(f"\r{self.description}: |{bar}| {percent:.0%}", end="", flush=True)
        if current == self.total:
            print()


class ColoredOutput:
    def __init__(self):
        self.use_color = self._supports_color()
        self.color_scheme = {
            "bold": "\033[1m" if self.use_color else "",
            "underline": "\033[4m" if self.use_color else "",
            "green": "\033[32m" if self.use_color else "",
            "yellow": "\033[33m" if self.use_color else "",
            "blue": "\033[34m" if self.use_color else "",
            "red": "\033[31m" if self.use_color else "",
            "reset": "\033[0m" if self.use_color else "",
        }

    def _supports_color(self):
        """
        Returns True if the running system's terminal supports color,
        and False otherwise.
        """
        plat = sys.platform
        supported_platform = plat != "Pocket PC" and (
            plat != "win32" or "ANSICON" in os.environ
        )

        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        if plat == "win32":
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                return kernel32.GetConsoleMode(kernel32.GetStdHandle(-11)) != 0
            except:
                return False

        return supported_platform and is_a_tty

    def set_color_scheme(self, color_scheme: Dict[str, str]):
        if self.use_color:
            self.color_scheme.update(color_scheme)

    def _colorize(self, text: str, color: str) -> str:
        if self.use_color:
            return (
                f"{self.color_scheme.get(color, '')}{text}{self.color_scheme['reset']}"
            )
        return text

    def bold(self, text: str) -> str:
        return self._colorize(text, "bold")

    def underline(self, text: str) -> str:
        return self._colorize(text, "underline")

    def green(self, text: str) -> str:
        return self._colorize(text, "green")

    def yellow(self, text: str) -> str:
        return self._colorize(text, "yellow")

    def blue(self, text: str) -> str:
        return self._colorize(text, "blue")

    def red(self, text: str) -> str:
        return self._colorize(text, "red")

    def custom_color(self, text: str, color: str) -> str:
        return self._colorize(text, color)
