import os
import openai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CopilotTestGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_from_csv(self, csv_path: str, output_dir: str = "tests/generated"):
        # Read CSV
        with open(csv_path, 'r') as f:
            csv_content = f.read()

        # Read prompt template
        with open("utilities/copilot_prompt.md", 'r') as f:
            prompt = f.read().replace("{input_csv}", csv_content)

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a test automation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower = More deterministic
        )

        # Extract code blocks from response
        generated_code = response.choices[0].message.content
        code_blocks = [
            block.replace("```python", "").replace("```", "").strip()
            for block in generated_code.split("```")
            if "python" in block
        ]

        # Save generated tests
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i, code in enumerate(code_blocks):
            test_path = Path(output_dir) / f"generated_test_{i}.py"
            with open(test_path, 'w') as f:
                f.write(code)
            print(f"✅ Generated: {test_path}")


# Example usage
if __name__ == "__main__":
    generator = CopilotTestGenerator()
    generator.generate_from_csv("test_cases/example_tests.csv")