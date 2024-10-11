from argonaut import Argonaut

def main():
    parser = Argonaut(description="Pet Care Manager - List Pets")
    parser.add("--verbose", action="store_true", help="Show detailed pet information")

    args = parser.parse()
    
    # Simulated pet list
    pets = ["Fluffy the Cat", "Rex the Dog", "Goldie the Fish"]
    
    print("Your Pets:")
    for index, pet in enumerate(pets, start=1):
        if args["verbose"]:
            print(f"{index}. {pet} - A lovely companion!")
        else:
            print(f"{index}. {pet}")

if __name__ == "__main__":
    main()