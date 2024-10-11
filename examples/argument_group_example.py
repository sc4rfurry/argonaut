from argonaut import Argonaut

def main():
    parser = Argonaut(description="Argument Group Example")
    group = parser.add_group("User Options", "Options related to user settings")
    group.add("--username", help="Your username")
    group.add("--password", help="Your password")

    args = parser.parse()
    print(f"Username: {args['username']}, Password: {args['password']}")

if __name__ == "__main__":
    main()