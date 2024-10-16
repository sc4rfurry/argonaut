# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut import Argonaut


def main():
    parser = Argonaut(description="Argument Groups Example")

    # Create argument groups
    input_group = parser.add_group("Input options")
    input_group.add("--input-file", "-i", help="Input file path")
    input_group.add(
        "--input-format",
        choices=["json", "yaml", "csv"],
        default="json",
        help="Input file format",
    )

    output_group = parser.add_group("Output options")
    output_group.add("--output-file", "-o", help="Output file path")
    output_group.add(
        "--output-format",
        choices=["json", "yaml", "csv"],
        default="json",
        help="Output file format",
    )

    # Create a mutually exclusive group
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add("--quiet", "-q", action="store_true", help="Suppress output")
    verbosity_group.add(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse()

    print(f"Input file: {args.get('input_file', 'Not specified')}")
    print(
        f"Input format: {args.get('input_format', 'json')}"
    )  # Use get() with a default value
    print(f"Output file: {args.get('output_file', 'Not specified')}")
    print(
        f"Output format: {args.get('output_format', 'json')}"
    )  # Use get() with a default value
    print(f"Quiet mode: {'Enabled' if args.get('quiet') else 'Disabled'}")
    print(f"Verbose mode: {'Enabled' if args.get('verbose') else 'Disabled'}")


if __name__ == "__main__":
    main()
