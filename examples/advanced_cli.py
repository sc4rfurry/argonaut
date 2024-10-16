# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut import Argonaut, ArgonautLogger, LogLevel
from argonaut.fancy_output import ProgressBar, ColoredOutput
from argonaut.utils import get_input_with_autocomplete
import time


def main():
    parser = Argonaut(description="Advanced CLI Example")
    logger = ArgonautLogger.get_logger("AdvancedCLI", level=LogLevel.INFO)
    colored_output = ColoredOutput()

    parser.add("--input", "-i", required=True, help="Input file")
    parser.add("--output", "-o", help="Output file")
    parser.add("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse()

    if args.get("verbose"):
        logger.set_level(LogLevel.DEBUG)

    logger.info("Starting advanced CLI example")

    # Use colored output
    colored_output.print("Welcome to the Advanced CLI Example!", color="green")

    # Use autocomplete for user input
    choices = ["option1", "option2", "option3"]
    user_choice = get_input_with_autocomplete("Choose an option: ", choices)
    print(f"You chose: {user_choice}")

    # Use progress bar
    print("Processing...")
    progress_bar = ProgressBar(total=100)
    for i in range(100):
        time.sleep(0.05)
        i = i + 1
        progress_bar.update(1)
    print("\nProcessing complete!")

    logger.debug("Advanced CLI example completed successfully")


if __name__ == "__main__":
    main()
