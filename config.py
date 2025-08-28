import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for environment variables."""

    # Azure credentials
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")

    # Google Gemini API key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Microsoft Graph scopes
    GRAPH_SCOPES: list[str] = ["https://graph.microsoft.com/.default"]

    @classmethod
    def validate(cls) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            ("AZURE_CLIENT_ID", cls.AZURE_CLIENT_ID),
            ("AZURE_CLIENT_SECRET", cls.AZURE_CLIENT_SECRET),
            ("AZURE_TENANT_ID", cls.AZURE_TENANT_ID),
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY),
        ]
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
