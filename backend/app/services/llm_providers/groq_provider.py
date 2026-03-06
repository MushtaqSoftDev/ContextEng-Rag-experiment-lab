from typing import AsyncGenerator
from groq import AsyncGroq

from .base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key) if api_key else None

    async def stream_chat(
        self,
        messages: list,
        temperature: float,
        top_p: float,
        max_tokens: int,
        reasoning_prefix: str,
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "[Error: GROQ_API_KEY not set]"
            return
        full_messages = []
        if reasoning_prefix:
            full_messages.append({"role": "user", "content": reasoning_prefix})
            full_messages.append({"role": "assistant", "content": "Understood."})
        full_messages.extend(messages)
        stream = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=full_messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
