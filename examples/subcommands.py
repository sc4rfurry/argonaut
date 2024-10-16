# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut import Argonaut


def main():
    parser = Argonaut(description="Subcommands Example")

    # Global arguments
    parser.add_global_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Add subcommands
    create = parser.add_subcommand("create", description="Create a new item")
    create.add("--name", required=True, help="Name of the item")

    delete = parser.add_subcommand("delete", description="Delete an existing item")
    delete.add("--id", required=True, type=int, help="ID of the item to delete")

    args = parser.parse()

    if args.get("verbose"):
        print("Verbose mode enabled")

    if args.get("subcommand") == "create":
        print(f"Creating item: {args['name']}")
    elif args.get("subcommand") == "delete":
        print(f"Deleting item with ID: {args['id']}")


if __name__ == "__main__":
    main()
