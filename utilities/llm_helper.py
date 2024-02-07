from utilities.env_helper   import EnvHelper
from utilities.observability_helper import ObservabilityHelper

import openai


class LLMHelper:
    def __init__(self):
        env_helper: EnvHelper = EnvHelper()

        # Configure OpenAI API
        openai.api_type    = "azure"
        openai.api_version = env_helper.AZURE_OPENAI_API_VERSION
        openai.api_base    = env_helper.OPENAI_API_BASE
        openai.api_key     = env_helper.OPENAI_API_KEY
        
        self.llm_model = env_helper.AZURE_OPENAI_MODEL
        self.llm_max_tokens = env_helper.AZURE_OPENAI_MAX_TOKENS if env_helper.AZURE_OPENAI_MAX_TOKENS != '' else None
        self.embedding_model = env_helper.AZURE_OPENAI_EMBEDDING_MODEL

        self.observability_helper = ObservabilityHelper()

        
    def get_completion(self, prompt):
        return "completion is nice"
    