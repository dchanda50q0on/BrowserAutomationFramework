import argparse
from utilities.copilot_generator import CopilotTestGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate tests using GitHub Copilot")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("--output", default="tests/generated", help="Output directory")

    args = parser.parse_args()

    print("🚀 Generating tests with Copilot...")
    generator = CopilotTestGenerator()
    generator.generate_from_csv(args.csv_file, args.output)


if __name__ == "__main__":
    main()