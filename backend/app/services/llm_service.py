import requests

from app.core.config import settings
from app.prompts.healthcare_prompt import build_healthcare_prompt


def generate_response(question: str, context: str = "") -> str:
    if not question.strip():
        return "Please enter a healthcare-related question."

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": build_healthcare_prompt(question, context),
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.15
        }
    }

    try:
        response = requests.post(
            settings.OLLAMA_URL,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return (
                f"LLM service error: {response.status_code} - "
                f"{response.text}"
            )

        data = response.json()
        return data.get("response", "No response generated.")

    except requests.exceptions.RequestException as error:
        return f"LLM service error: {str(error)}"