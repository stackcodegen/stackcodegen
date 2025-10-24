import anthropic
from pprint import pprint
from src.llm.base import LLMClient
from src.llm.response_format import LLMResponse, AssistantMessage


class AnthropicClient(LLMClient):
    def __init__(self, model, api_key, temperature, max_tokens):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(api_key=api_key)

    def call(self, messages: list[dict], **kwargs) -> LLMResponse:
        system_message = ""
        if messages and messages[0]["role"] == "system":
            system_message = messages[0]["content"]
            messages = messages[1:]  # remove the top system message

        llm_response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_message,
            messages=messages,
        )

        content = llm_response.content[0].text

        usage = getattr(llm_response, "usage", {})
        token_usage = {
            "input_tokens": usage.input_tokens if hasattr(usage, "input_tokens") else usage.get("input_tokens", 0),
            "output_tokens": usage.output_tokens if hasattr(usage, "output_tokens") else usage.get("output_tokens", 0),
            "total_tokens": (
                    (usage.input_tokens if hasattr(usage, "input_tokens") else usage.get("input_tokens", 0)) +
                    (usage.output_tokens if hasattr(usage, "output_tokens") else usage.get("output_tokens", 0))
            )
        }

        return LLMResponse(
            message=AssistantMessage(content=content),
            token_usage=token_usage,
            raw=llm_response.model_dump() if hasattr(llm_response, "model_dump") else llm_response.dict()
        )
