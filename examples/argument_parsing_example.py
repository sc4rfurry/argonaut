from argonaut import Argonaut

def main():
    parser = Argonaut(description="Argument Parsing Example")
    parser.add("--name", help="Your name")
    parser.add("--age", type=int, help="Your age")
    parser.add("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse()

    if args["verbose"]:
        print(f"Verbose mode enabled.")
    print(f"Hello, {args['name']}! You are {args['age']} years old.")

if __name__ == "__main__":
    main()