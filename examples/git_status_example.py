from argonaut import Argonaut

def main():
    parser = Argonaut(description="Git Status Example")
    parser.add("--short", action="store_true", help="Show a short status")
    parser.add("--porcelain", action="store_true", help="Show a porcelain status")

    args = parser.parse()
    
    print("Checking repository status...")
    if args["short"]:
        print("Short status: [A] Added, [M] Modified")
    elif args["porcelain"]:
        print("Porcelain status: [M] Modified, [D] Deleted")
    else:
        print("Full status: Showing detailed information about changes.")

if __name__ == "__main__":
    main()