from pprint import pprint
import requests
from pydantic import BaseModel

from src.llm.base import LLMClient
from src.llm.response_format import AssistantMessage, LLMResponse


class OllamaClient(LLMClient):
    def __init__(self, model, base_url: str = "http://localhost:11434", temperature: float = 0.5,
                 max_tokens: int = 6000):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(self, messages: list[dict], **kwargs) -> LLMResponse:

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "options": {
                "num_predict": self.max_tokens if self.max_tokens > 0 else None,
                "seed": 42,

            },
            "stream": False
        }

        if "format" in kwargs:
            fmt = kwargs["format"]
            if isinstance(fmt, type) and issubclass(fmt, BaseModel):
                payload["format"] = fmt.model_json_schema()
            else:
                payload["format"] = fmt
        try:
            llm_response = requests.post(url, json=payload)
            llm_response.raise_for_status()

            data = llm_response.json()
            content = data.get("message", {}).get("content", "")
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)
            token_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }

            response = LLMResponse(
                message=AssistantMessage(content=content),
                token_usage=token_usage,
                raw=data
            )
            return response

        except Exception as e:
            raise RuntimeError(f"Ollama API call failed: {e}")
