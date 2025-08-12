from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    def __init__(self, name: str, **kwargs):
        self.name = name

    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Any:
        pass
