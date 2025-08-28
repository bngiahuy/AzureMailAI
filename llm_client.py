import logging
from typing import Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Google Gemini LLM."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-lite"
        self.system_instruction = """
You are an intelligent assistant specialized in email summarization. Given the content of an email, generate a concise and clear summary that captures the main points, important details, and any action items. Ensure the summary is easy to understand and preserves the original intent of the message. Do not include unnecessary information or personal opinions. Reply in Markdown format, use the same language as the email.
"""

    def invoke_llm(self, prompt: str) -> Optional[str]:
        """
        Invoke the LLM with the given prompt and return the response.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    max_output_tokens=1024,
                    temperature=0.7,
                    seed=23,
                ),
            )

            if not response or not response.text:
                logger.warning("No response from LLM.")
                return None

            return response.text

        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            return None
