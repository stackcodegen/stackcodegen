from openai import OpenAI

from src.llm.base import LLMClient
from src.llm.response_format import LLMResponse, AssistantMessage


class OpenAIClient(LLMClient):
    def __init__(self, model, api_key, temperature, max_tokens):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key)

    def call(self, messages: list[dict], **kwargs) -> LLMResponse:
        response_format = kwargs.get("format")  # Might be None

        if response_format:
            # Structured (pydantic) parsing
            llm_response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
                seed=42
            )

        else:
            llm_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                seed=42
            )

        content = llm_response.choices[0].message.content
        usage = getattr(llm_response, "usage", {})
        token_usage = {
            "input_tokens": usage.prompt_tokens if hasattr(usage, "prompt_tokens") else usage.get("prompt_tokens"),
            "output_tokens": usage.completion_tokens if hasattr(usage, "completion_tokens") else usage.get(
                "completion_tokens"),
            "total_tokens": usage.total_tokens if hasattr(usage, "total_tokens") else usage.get("total_tokens")
        }

        return LLMResponse(
            message=AssistantMessage(content=content),
            token_usage=token_usage,
            raw=llm_response.model_dump() if hasattr(llm_response, "model_dump") else llm_response.dict()
        )
