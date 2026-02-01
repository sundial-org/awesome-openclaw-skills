import argparse
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types


def run_vision_sandbox(image_path, prompt, model_id="gemini-3-flash-preview"):
    """
    Executes a vision task using Gemini's native code execution sandbox.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    image_file = Path(image_path)
    if not image_file.exists():
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Load image
    with open(image_path, "rb") as f:
        image_data = f.read()

    mime_type = (
        "image/jpeg" if image_file.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
    )
    image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)

    # Configure model with code execution
    config = types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
        temperature=0.0,
    )

    print(f"--- Sending request to {model_id} ---")

    try:
        response = client.models.generate_content(
            model=model_id, contents=[prompt, image_part], config=config
        )
    except Exception as e:
        print(f"Error during API call: {e}")
        sys.exit(1)

    if not response.candidates:
        print("No candidates returned from model.")
        return

    # Process response parts
    for part in response.candidates[0].content.parts:
        if part.executable_code:
            print("\n--- SANDBOX CODE ---")
            print(f"```python\n{part.executable_code.code}\n```")

        if part.code_execution_result:
            print("\n--- SANDBOX OUTPUT ---")
            print(f"```\n{part.code_execution_result.output}\n```")

        if part.text:
            print("\n--- MODEL RESPONSE ---")
            print(part.text)

    # Extract inline images if generated
    for i, candidate in enumerate(response.candidates):
        for j, part in enumerate(candidate.content.parts):
            if hasattr(part, "inline_data") and part.inline_data:
                out_path = f"sandbox_output_{i}_{j}.png"
                with open(out_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"\nMEDIA: {os.path.abspath(out_path)}")


def main():
    parser = argparse.ArgumentParser(
        description="Vision Sandbox: Gemini Agentic Vision Executor"
    )
    parser.add_argument("-i", "--image", required=True, help="Path to input image")
    parser.add_argument(
        "-p", "--prompt", required=True, help="Instruction for the model"
    )
    parser.add_argument(
        "-m", "--model", default="gemini-3-flash-preview", help="Model ID"
    )

    args = parser.parse_args()
    run_vision_sandbox(args.image, args.prompt, args.model)


if __name__ == "__main__":
    main()
