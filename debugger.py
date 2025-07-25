
import google.generativeai as genai
from utils import strip_code_fence
genai.configure(api_key="AIzaSyB1lEOunVZHFS3D7tTpQAVG_B7oietpc_E")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
def debug_code(task_prompt: str, feedback_summary: str, language: str) -> str:
    """
    Regenerates improved code using Gemini,
    using test case feedback to improve it, supporting multiple languages.
    """
    try:
        prompt = (
            f"You are a debugging assistant for the {language.capitalize()} programming language.\n"
            f"Regenerate complete {language.capitalize()} code to solve the following task.\n"
            f"Use standard input/output. No markdown, explanation, or comments.\n\n"
            f"Task: {task_prompt.strip()}\n\n"
            f"Here is feedback from the last run:\n{feedback_summary.strip()}\n\n"
            f"Please provide improved complete executable {language.capitalize()} code."
        )
        response = model.generate_content(prompt)
        raw_code = response.text.strip()
        return strip_code_fence(raw_code)
    except Exception as e:
        print("Gemini API error during debug:", e)
        return '''
def main():
    print("Gemini failed during debug step.")
if __name__ == "__main__":
    main()
'''