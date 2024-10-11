from argonaut import Argonaut
from argonaut.exceptions import ArgonautValidationError

def main():
    parser = Argonaut(description="Git Commit Example")
    
    # Add the required commit message argument
    parser.add("--message", "-m", help="Commit message", required=True)
    
    # Add the amend argument
    parser.add("--amend", action="store_true", help="Amend the previous commit")

    args = parser.parse()
    
    # Check if 'amend' is in args to avoid KeyError
    if "amend" in args and args["amend"]:
        print("Amending the previous commit...")
    
    print(f"Committing changes with message: '{args['message']}'")

if __name__ == "__main__":
    main()