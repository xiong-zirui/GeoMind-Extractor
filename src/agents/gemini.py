import google.generativeai as genai
from typing import Any
from agents.base import BaseAgent

class GeminiAgent(BaseAgent):
    def __init__(self, name: str, api_key: str, **kwargs):
        super().__init__(name, **kwargs)
        if not api_key or "YOUR_OPENAI_API_KEY" in api_key:
            raise ValueError("ERROR: API key not found or not set in config.yml.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(name)

    def process(self, input_data: list, **kwargs) -> Any:
        return self.model.generate_content(input_data)

    def upload_file(self, file_path, display_name):
        return genai.upload_file(path=file_path, display_name=display_name)

    def delete_file(self, file_name):
        genai.delete_file(file_name)
