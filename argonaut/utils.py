try:
    import readline

    has_readline = True
except ImportError:
    has_readline = False
from typing import List


def get_input_with_autocomplete(prompt: str, choices: List[str]) -> str:
    if has_readline:

        def completer(text: str, state: int) -> str:
            options = [choice for choice in choices if choice.startswith(text)]
            return options[state] if state < len(options) else None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    user_input = input(prompt)

    if has_readline:
        readline.set_completer(None)

    return user_input


def sanitize_input(input_str: str) -> str:
    return input_str.replace(";", "").replace("&", "").replace("|", "")
