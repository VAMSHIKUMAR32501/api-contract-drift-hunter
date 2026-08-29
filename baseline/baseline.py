from pathlib import Path
from ollama import chat


MODEL = "qwen3:1.7b"


def load_prompt():
    prompt_path = Path(__file__).parent / "prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def load_case(case_path):
    case_path = Path(case_path)

    openapi = (case_path / "openapi.yaml").read_text(encoding="utf-8")
    source = (case_path / "app.py").read_text(encoding="utf-8")

    return openapi, source


def analyze_case(case_path):
    openapi, source = load_case(case_path)
    prompt = load_prompt()

    user_message = f"""
{prompt}

IMPORTANT:
Analyze only the API contract and source code below.
Do not use expected.json.
Do not modify the source code.

OPENAPI SPECIFICATION:
----------------------
{openapi}

SOURCE CODE:
------------
{source}
"""

    response = chat(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": user_message
        }
    ],
    think=False,
    format="json",
    options={
        "temperature": 0
    }
)

    return response.message.content


if __name__ == "__main__":
    print("Running baseline on Case 01...")

    result = analyze_case("benchmark/case01")

    print("\n===== BASELINE RESULT =====\n")
    print(result)