import os
import json
from abc import ABC, abstractmethod
import httpx # For making asynchronous HTTP requests
import google.generativeai as genai
from google.generativeai import GenerativeModel

class Config:
    """Centralized configuration for API keys and base URLs."""
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

class BaseLlm(ABC):
    """
    Abstract base class for a generic Language Model client.
    """
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    async def generate_content(self, prompt: str, tools: list = None) -> str:
        """
        Generates content from the language model.

        Args:
            prompt: The text prompt to send to the model.
            tools: An optional list of tool definitions the model can use.

        Returns:
            The raw text or JSON string response from the model.
        """
        pass

class GeminiLlm(BaseLlm):
    """
    LLM client for Google's Gemini models.
    """
    def __init__(self, model: str):
                super().__init__(model)
                if not Config.GOOGLE_API_KEY:
                    raise ValueError("GOOGLE_API_KEY environment variable not set.")
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                # For the planner agent, we want JSON output.
                # We can enforce this with generation config.
                generation_config = {
                    "response_mime_type": "application/json",
                }
                self.model_instance = GenerativeModel( # Use GenerativeModel directly
                    model_name=model, # Changed 'model' to 'model_name' for clarity and potential future compatibility
                    generation_config=generation_config
                )

    async def generate_content(self, prompt: str, tools: list = None) -> str:
        print(f"--- Calling Gemini (Model: {self.model}) ---")
        print(f"Prompt: {prompt[:100]}...")
        
        try:
            response = await self.model_instance.generate_content_async(prompt)
            # The response's text attribute should be a JSON string
            # due to the response_mime_type we configured.
            content = response.text
            print("--- Gemini responded ---")
            return content
        except Exception as e:
            print(f"An error occurred with the Gemini API: {e}")
            # Return a string that looks like a JSON error object
            return '{"error": "An error occurred with the Gemini API."}'


class ClaudeLlm(BaseLlm):
    """
    LLM client for Anthropic's Claude models via OpenRouter.
    """
    def __init__(self, model: str):
        super().__init__(model)
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable not set.")
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def generate_content(self, prompt: str, tools: list = None) -> str:
        print(f"--- Calling Claude (Model: {self.model}) via OpenRouter ---")
        print(f"Prompt: {prompt[:100]}...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000", # Optional: Replace with your actual app URL
            "X-Title": "Workflow Factory CLI", # Optional: Replace with your actual app name
        }

        messages = [{"role": "user", "content": prompt}]
        
        # OpenRouter API for chat completions
        # https://openrouter.ai/docs#chat-completions
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            # "tools": tools, # Add tools if they become relevant for Claude via OpenRouter
        }

        try:
            response = await self.client.post(
                "/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            
            # Extract content from the response
            # OpenRouter's response structure is similar to OpenAI's
            if data and data.get("choices"):
                content = data["choices"][0]["message"]["content"]
                print("--- Claude responded via OpenRouter ---")
                
                # We'll remove the mock debugging logic now that we have real APIs
                return content
            else:
                return "Error: No content in Claude response from OpenRouter."

        except httpx.HTTPStatusError as e:
            print(f"HTTP error with OpenRouter: {e.response.status_code} - {e.response.text}")
            return f"Error: HTTP {e.response.status_code} from OpenRouter."
        except httpx.RequestError as e:
            print(f"Network error with OpenRouter: {e}")
            return f"Error: Network issue connecting to OpenRouter."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"Error: {e}"
