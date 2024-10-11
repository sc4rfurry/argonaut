from argonaut import Argonaut

def main():
    parser = Argonaut(description="Git Push Example")
    parser.add("remote", help="Name of the remote repository")
    parser.add("branch", help="Name of the branch to push")

    args = parser.parse()
    
    print(f"Pushing changes to {args['remote']} on branch {args['branch']}...")

if __name__ == "__main__":
    main()