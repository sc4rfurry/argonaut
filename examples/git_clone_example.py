from argonaut import Argonaut

def main():
    parser = Argonaut(description="Git Clone Example")
    parser.add("repository", help="URL of the repository to clone")
    parser.add("--branch", help="Branch to clone")
    parser.add("--depth", type=int, help="Limit the clone to the specified number of commits")

    args = parser.parse()
    
    print(f"Cloning repository from {args['repository']}...")
    if args.get("branch"):
        print(f"Checking out branch: {args['branch']}")
    if args.get("depth"):
        print(f"Limiting clone to {args['depth']} commits.")

if __name__ == "__main__":
    main()