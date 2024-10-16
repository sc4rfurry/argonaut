# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut import Argonaut, ArgonautValidationError


def positive_integer(value):
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError("Value must be a positive integer")
        return int_value
    except ValueError:
        raise ArgonautValidationError("count", "Value must be a positive integer")


def valid_email(value):
    if "@" not in value or "." not in value.split("@")[1]:
        raise ArgonautValidationError("email", "Invalid email format")
    return value


def main():
    parser = Argonaut(description="Custom Validators Example")

    parser.add("--count", type=int, help="A positive integer").add_validator(
        positive_integer
    )
    parser.add("--email", help="A valid email address").add_validator(valid_email)

    try:
        args = parser.parse()
        print(f"Count: {args.get('count', 'Not specified')}")
        print(f"Email: {args.get('email', 'Not specified')}")
    except ArgonautValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
