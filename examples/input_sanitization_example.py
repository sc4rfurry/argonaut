from argonaut import Argonaut

def main():
    parser = Argonaut(description="Input Sanitization Example")
    parser.add("--input", help="Input string to sanitize")

    args = parser.parse()
    sanitized_input = args["input"].replace("<script>", "").replace("</script>", "")
    print(f"Sanitized input: {sanitized_input}")

if __name__ == "__main__":
    main()