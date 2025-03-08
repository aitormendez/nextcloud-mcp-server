from abc import ABC, abstractmethod
from typing import Dict, Optional
import os
from openai import OpenAI
from anthropic import Anthropic

class LLMProvider(ABC):
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, str]) -> str:
        """Process a query with the given context using the LLM provider."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
    def process_query(self, query: str, context: Dict[str, str]) -> str:
        # Format context into a string
        context_str = "\n\n".join([f"File: {k}\nContent:\n{v}" for k, v in context.items()])
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer questions based on the provided context."},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuery: {query}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
    def process_query(self, query: str, context: Dict[str, str]) -> str:
        context_str = "\n\n".join([f"File: {k}\nContent:\n{v}" for k, v in context.items()])
        
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"Context:\n{context_str}\n\nQuery: {query}"
            }]
        )
        return message.content[0].text

def get_llm_provider(provider_name: str = "openai", api_key: Optional[str] = None) -> LLMProvider:
    """Factory function to get the appropriate LLM provider."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: {list(providers.keys())}")
    
    return providers[provider_name](api_key=api_key)