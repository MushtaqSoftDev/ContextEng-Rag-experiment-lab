from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMProvider(ABC):
    @abstractmethod
    async def stream_chat(
        self,
        messages: list,
        temperature: float,
        top_p: float,
        max_tokens: int,
        reasoning_prefix: str,
    ) -> AsyncGenerator[str, None]:
        pass


def get_llm_provider(
    provider: str,
    openai_api_key: str = "",
    groq_api_key: str = "",
    deepseek_api_key: str = "",
) -> BaseLLMProvider:
    provider = (provider or "").lower()
    if provider == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=openai_api_key)
    if provider == "groq":
        from .groq_provider import GroqProvider
        return GroqProvider(api_key=groq_api_key)
    if provider == "deepseek":
        from .deepseek_provider import DeepSeekProvider
        return DeepSeekProvider(api_key=deepseek_api_key)
    if provider == "huggingface":
        from .huggingface_provider import HuggingFaceProvider
        return HuggingFaceProvider()
    raise ValueError(f"Unknown provider: {provider}")
