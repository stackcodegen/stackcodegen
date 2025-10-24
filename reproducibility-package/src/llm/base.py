from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    @abstractmethod
    def call(self, messages: Any, response_format=Any):
        pass
