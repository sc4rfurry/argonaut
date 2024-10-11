from argonaut import Argonaut

def main():
    parser = Argonaut(description="Pet Care Manager - Add a Pet")
    parser.add("name", help="Name of your pet")
    parser.add("--type", help="Type of pet (e.g., dog, cat, fish)")
    
    args = parser.parse()
    
    print(f"You've added a new pet! Meet {args['name']}, the {args.get('type', 'unknown type')}!")

if __name__ == "__main__":
    main()