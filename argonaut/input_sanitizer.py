# /usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import html
import os
from typing import Any, Union
import pathlib


def sanitize_input(input_str: Union[str, Any]) -> str:
    if not isinstance(input_str, str):
        return str(input_str)

    # Remove potentially dangerous shell characters
    sanitized = re.sub(r"[;&|`$]", "", input_str)
    # Remove any HTML tags
    sanitized = re.sub(r"<[^>]*?>", "", sanitized)
    # Escape any remaining HTML entities
    sanitized = html.escape(sanitized)
    # Unescape the sanitized input to preserve original characters
    sanitized = html.unescape(sanitized)
    # Remove any null bytes
    sanitized = sanitized.replace("\0", "")
    # Limit the length of the input
    max_length = 1000  # You can adjust this value as needed
    sanitized = sanitized[:max_length]
    return sanitized.strip()


def sanitize_filename(filename: str) -> str:
    # Remove any directory traversal attempts
    sanitized = os.path.basename(filename)
    # Remove any non-alphanumeric characters except for periods, hyphens, and underscores
    sanitized = re.sub(r"[^\w\-_\.]", "", sanitized)
    return sanitized


def sanitize_path(path: str) -> str:
    # Use pathlib for cross-platform path handling
    sanitized = pathlib.Path(path).resolve()
    allowed_dir = pathlib.Path.cwd()
    if not str(sanitized).startswith(str(allowed_dir)):
        raise ValueError("Path is outside of the allowed directory")
    return str(sanitized)
