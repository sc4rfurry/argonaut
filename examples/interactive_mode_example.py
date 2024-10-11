from argonaut import Argonaut

def main():
    parser = Argonaut(description="Interactive Mode Example")
    parser.add("--name", help="Your name")

    args = parser.interactive()
    print(f"Hello, {args['name']}!")

if __name__ == "__main__":
    main()