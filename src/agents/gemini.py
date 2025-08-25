import google.generativeai as genai
from typing import Any
from agents.base import BaseAgent

class GeminiClientSingleton:
    """Singleton to ensure genai is configured only once."""
    _instance = None
    _configured = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def configure(cls, api_key: str):
        """Configure genai only once."""
        if not cls._configured:
            if not api_key or "YOUR_OPENAI_API_KEY" in api_key:
                raise ValueError("ERROR: API key not found or not set in config.yml.")
            genai.configure(api_key=api_key)
            cls._configured = True

class GeminiAgent(BaseAgent):
    def __init__(self, name: str, api_key: str, **kwargs):
        super().__init__(name, **kwargs)
        # Use singleton to configure genai only once
        GeminiClientSingleton.configure(api_key)
        self.model = genai.GenerativeModel(name)

    def process(self, input_data: list, **kwargs) -> Any:
        return self.model.generate_content(input_data)

    def upload_file(self, file_path, display_name):
        return genai.upload_file(path=file_path, display_name=display_name)

    def delete_file(self, file_name):
        genai.delete_file(file_name)
