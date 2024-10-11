from argonaut import Argonaut

def get_default_age():
    return 30  # Dynamic default value

def main():
    parser = Argonaut(description="Dynamic Default Example")
    parser.add("--age", type=int, default=get_default_age, help="Your age")

    args = parser.parse()
    print(f"Your age is {args.get('age', 'not provided')}.")
    
if __name__ == "__main__":
    main()