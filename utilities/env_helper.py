"""Manages environment variables."""
import os

from dotenv import load_dotenv

class EnvHelper:
    """Manages environment variables."""

    ENV_FILE = ".env"

    def __init__(self) -> None:
        """Load ENV."""
        self.load_vars()

    def load_vars(self):
        load_dotenv(EnvHelper.ENV_FILE)

    # Azure OpenAI - TO BE CONFIGURED FROM PAGE
        self.AZURE_OPENAI_RESOURCE_NAME         = os.getenv('AZURE_OPENAI_RESOURCE_NAME', '')
        self.AZURE_OPENAI_KEY                   = os.getenv('AZURE_OPENAI_KEY', '')
        self.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT_NAME', '')
        self.AZURE_OPENAI_API_VERSION           = os.getenv('AZURE_OPENAI_API_VERSION', '')

    # Set env for OpenAI SDK
        self.OPENAI_API_BASE = f"https://{self.AZURE_OPENAI_RESOURCE_NAME}.openai.azure.com/"
        self.OPENAI_API_KEY = self.AZURE_OPENAI_KEY
        self.OPENAI_API_VERSION = self.AZURE_OPENAI_API_VERSION

        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = self.OPENAI_API_BASE
        os.environ["OPENAI_API_KEY"] = self.AZURE_OPENAI_KEY
        os.environ["OPENAI_API_VERSION"] = self.AZURE_OPENAI_API_VERSION

    
    def update_env_variable(self, variable_name, variable_value):
        # Attempt to read the current content of the .env file
        env_vars = {}
        try:
            with open(EnvHelper.ENV_FILE, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        except FileNotFoundError:
            pass  # It's okay if the file does not exist yet

        # Update the specified environment variable
        env_vars[variable_name] = variable_value

        # Write the updates back to the .env file
        with open(EnvHelper.ENV_FILE, 'w') as file:
            for key, value in env_vars.items():
                file.write(f'{key}={value}\n')

        self.load_vars()