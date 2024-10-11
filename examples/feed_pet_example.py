from argonaut import Argonaut

def main():
    parser = Argonaut(description="Pet Care Manager - Feed a Pet")
    parser.add("index", type=int, help="Index of the pet to feed")

    args = parser.parse()
    
    # Simulated pet list
    pets = ["Fluffy the Cat", "Rex the Dog", "Goldie the Fish"]
    
    if 0 < args["index"] <= len(pets):
        print(f"You fed {pets[args['index'] - 1]}! They are so happy!")
    else:
        print("Invalid pet index! Please try again.")

if __name__ == "__main__":
    main()