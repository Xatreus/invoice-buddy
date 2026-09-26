from invoice_buddy.agent import get_tool_schemas


def main():
    schemas = get_tool_schemas()

    print("Registered agent tools:")
    print()

    for schema in schemas:
        print(
            "-",
            schema["function"]["name"],
        )

    print()
    print(f"Total tools: {len(schemas)}")


if __name__ == "__main__":
    main()
