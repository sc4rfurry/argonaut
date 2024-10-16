# /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from argonaut import Argonaut
from argonaut.decorators import env_var


def main():
    parser = Argonaut(description="Environment Variables Example")

    parser.add(
        "--api-key",
        env_var="API_KEY",
        help="API key (can be set via API_KEY environment variable)",
    )
    parser.add(
        "--debug",
        env_var="DEBUG",
        action="store_true",
        help="Enable debug mode (can be set via DEBUG environment variable)",
    )

    # Set some environment variables for testing
    os.environ["API_KEY"] = "test_api_key"
    os.environ["DEBUG"] = "1"

    args = parser.parse()

    print(f"API Key: {args.get('api_key', 'Not set')}")
    print(f"Debug mode: {'Enabled' if args.get('debug') else 'Disabled'}")


if __name__ == "__main__":
    main()
