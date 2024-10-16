# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut import Argonaut


def main():
    parser = Argonaut(description="Basic CLI Tool Example")

    parser.add("--name", help="Your name")
    parser.add("--age", type=int, help="Your age")
    parser.add("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse()

    if args.get("verbose"):
        print("Verbose mode enabled")

    print(f"Hello, {args.get('name', 'Anonymous')}!")
    if args.get("age"):
        print(f"You are {args['age']} years old.")


if __name__ == "__main__":
    main()
