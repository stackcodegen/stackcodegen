import os

from src.config.loader import ConfigLoader
from src.llm.antrhopic_client import AnthropicClient
from src.llm.openai_client import OpenAIClient
from src.llm.ollama_client import OllamaClient


class ModelFactory:
    def __init__(self, config: ConfigLoader, model_name: str = None):
        self.config = config
        self.active_model = model_name or os.getenv("MODEL_PROFILE") or config.default_model
        self.model_config = config.get_model_config(self.active_model)

    def get_model_client(self):
        provider = self.model_config.provider
        model_name = self.model_config.name
        temperature = self.model_config.temperature
        max_tokens = self.model_config.max_tokens if self.model_config.max_tokens > 0 else None

        if provider == "openai":
            return OpenAIClient(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider == "ollama":
            return OllamaClient(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider == "anthropic":
            return AnthropicClient(
                model=model_name,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
