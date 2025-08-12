from typing import Any, Dict

from agents.base import BaseAgent
from agents.gemini import GeminiAgent
# Placeholder for other agent types
# from agents.ollama import OllamaAgent 
# from agents.hf import HuggingFaceAgent

class AgentManager:
    def __init__(self, agent_name: str, agent_type: str, **kwargs):
        self.agent_types = {
            "gemini": GeminiAgent,
            # "ollama": OllamaAgent,
            # "hf": HuggingFaceAgent,
        }
        self.agent_type = agent_type.lower()
        if self.agent_type not in self.agent_types:
            raise ValueError(f"Invalid agent type. Must be one of: {', '.join(self.agent_types.keys())}")

        agent_class = self.agent_types[self.agent_type]
        self.agent = agent_class(agent_name, **kwargs)

    def process_input(self, input_data: Any, **kwargs) -> Any:
        return self.agent.process(input_data, **kwargs)

    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.agent.name,
            "type": type(self.agent).__name__,
        }

    def __getattr__(self, name):
        """Delegate other methods to the underlying agent."""
        if hasattr(self.agent, name):
            return getattr(self.agent, name)
        raise AttributeError(f"'{type(self.agent).__name__}' object has no attribute '{name}'")
