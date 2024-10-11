from argonaut import Argonaut

def main():
    parser = Argonaut(description="Shell Completion Example")
    parser.add("--verbose", help="Enable verbose output")
    parser.add("--count", type=int, help="Count of items")

    # Generate completion script for bash
    parser.add_completion("bash")

    print("Shell completion script generated for bash.")

if __name__ == "__main__":
    main()