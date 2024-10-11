from argonaut import Argonaut

def main():
    parser = Argonaut(description="Pet Care Manager - Remove a Pet")
    parser.add("index", type=int, help="Index of the pet to remove")

    args = parser.parse()
    
    # Simulated pet list
    pets = ["Fluffy the Cat", "Rex the Dog", "Goldie the Fish"]
    
    if 0 < args["index"] <= len(pets):
        removed_pet = pets.pop(args["index"] - 1)
        print(f"{removed_pet} has been removed from your pet list!")
    else:
        print("Invalid pet index! Please try again.")

if __name__ == "__main__":
    main()