from llm_client import LLMClient
from config import Config

# Initialize LLM client with config
llm_client = LLMClient(Config.GEMINI_API_KEY)


def invoke_llm(prompt: str) -> str | None:
    """Wrapper function for backward compatibility."""
    return llm_client.invoke_llm(prompt)
