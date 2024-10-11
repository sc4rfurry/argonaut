from argonaut import Argonaut
import os

def main():
    os.environ["DEFAULT_NAME"] = "John Doe"  # Set an environment variable for demonstration
    parser = Argonaut(description="Environment Variable Example")
    parser.add("--name", env_var="DEFAULT_NAME", help="Your name")

    args = parser.parse()
    print(f"Hello, {args['name']}!")

if __name__ == "__main__":
    main()