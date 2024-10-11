from argonaut import Argonaut, ArgonautValidationError

def main():
    parser = Argonaut(description="Error Handling Example")
    parser.add("--age", type=int, required=True, help="Your age")

    try:
        args = parser.parse()
        print(f"Your age is {args['age']}.")
    except ArgonautValidationError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()