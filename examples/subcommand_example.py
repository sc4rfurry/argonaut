from argonaut import Argonaut

def main():
    parser = Argonaut(description="Subcommand Example")
    subcommand = parser.add_subcommand("greet", help="Greet someone")
    subcommand.add("--name", help="Name of the person to greet")

    args = parser.parse()

    if args["subcommand"] == "greet":
        print(f"Hello, {args['name']}!")

if __name__ == "__main__":
    main()