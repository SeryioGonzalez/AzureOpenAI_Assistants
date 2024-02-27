"""Manages environment variables."""
import os

from dotenv import load_dotenv

class EnvHelper:
    """Manages environment variables."""

    def __init__(self) -> None:
        """Load ENV."""
        load_dotenv()

        # Azure OpenAI
        self.AZURE_OPENAI_RESOURCE = os.getenv('AZURE_OPENAI_RESOURCE', '')
        self.AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL', '')
        self.AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY', '')
        self.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT_NAME', '')
        self.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')

    # Set env for OpenAI SDK
        self.OPENAI_API_BASE = f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/"
        self.OPENAI_API_KEY = self.AZURE_OPENAI_KEY
        self.OPENAI_API_VERSION = self.AZURE_OPENAI_API_VERSION

        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/"
        os.environ["OPENAI_API_KEY"] = self.AZURE_OPENAI_KEY
        os.environ["OPENAI_API_VERSION"] = self.AZURE_OPENAI_API_VERSION
