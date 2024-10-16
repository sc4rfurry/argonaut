# /usr/bin/env python3
# -*- coding: utf-8 -*-
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
        # Check for NO_COLOR environment variable
        if "NO_COLOR" in os.environ:
            return False

        # Check for FORCE_COLOR environment variable
        if "FORCE_COLOR" in os.environ:
            return True

        # Windows detection
        if sys.platform == "win32":
            return self._supports_color_win()

        # Unix-like systems
        return self._supports_color_unix()

    def _supports_color_win(self):
        try:
            import winreg
        except ImportError:
            return False
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Console")
            return winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")[0] == 1
        except WindowsError:
            return False

    def _supports_color_unix(self):
        return sys.stdout.isatty() and (
            "COLORTERM" in os.environ
            or os.environ.get("TERM")
            in [
                "xterm",
                "xterm-color",
                "xterm-256color",
                "linux",
                "screen",
                "screen-256color",
                "tmux",
                "tmux-256color",
            ]
        )

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

    def print(self, text: str, color: str = "reset") -> None:
        print(self._colorize(text, color))
