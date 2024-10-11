import re
import html


def sanitize_input(input_str: str) -> str:
    # Remove potentially dangerous shell characters
    sanitized = re.sub(r"[;&|`$]", "", input_str)
    # Remove any HTML tags
    sanitized = re.sub(r"<[^>]*?>", "", sanitized)
    # Escape any remaining HTML entities
    sanitized = html.escape(sanitized)
    # Unescape the sanitized input to preserve original characters
    sanitized = html.unescape(sanitized)
    return sanitized.strip()
