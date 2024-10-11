from argonaut import Argonaut, ArgonautValidationError, ArgonautUnknownArgumentError

def validate_positive(value):
    """Validator to ensure the value is positive."""
    if int(value) <= 0:
        raise ValueError("Value must be positive")
    return True

def main():
    parser = Argonaut(description="Custom Validator Example")
    parser.add("--number", type=int, validator=validate_positive, help="A positive number")

    try:
        args = parser.parse()
        print(f"Your number is {args['number']}.")
    except ArgonautValidationError as e:
        print(f"Validation Error: {e}")
    except ArgonautUnknownArgumentError as e:
        print(f"Unknown Argument Error: {e}")

if __name__ == "__main__":
    main()