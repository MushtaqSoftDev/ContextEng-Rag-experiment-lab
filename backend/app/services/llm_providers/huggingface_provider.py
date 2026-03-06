"""
HuggingFace model - CPU only, free, no API key.
Uses flan-t5-large (better summarization & Q&A than base). For lighter CPU: flan-t5-base.
"""
from typing import AsyncGenerator
import asyncio

from .base import BaseLLMProvider


def _fix_t5_spaced_output(text: str) -> str:
    """Fix T5/Flan-T5 tokenizer artifact: 'd e p e n d e d' -> 'depended'.
    The tokenizer adds a space before each token when decoding, producing
    space-between-every-character output. Merge consecutive single-char parts."""
    parts = text.split()
    result = []
    current = []
    for p in parts:
        if len(p) == 1:
            current.append(p)
        else:
            if current:
                result.append("".join(current))
                current = []
            result.append(p)
    if current:
        result.append("".join(current))
    return " ".join(result)


class HuggingFaceProvider(BaseLLMProvider):
    _pipe = None
    _initialized = False

    @classmethod
    def _ensure_loaded(cls):
        if cls._initialized:
            return
        try:
            from transformers import pipeline
            # flan-t5-large: better quality than base, still CPU-viable
            # Options: flan-t5-small (80M), flan-t5-base (250M), flan-t5-large (780M), flan-t5-xl (3B)
            cls._pipe = pipeline(
                "text2text-generation",
                model="google/flan-t5-large",
                device=-1,  # CPU
            )
            cls._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}") from e

    async def stream_chat(
        self,
        messages: list,
        temperature: float,
        top_p: float,
        max_tokens: int,
        reasoning_prefix: str,
    ) -> AsyncGenerator[str, None]:
        def _run():
            self._ensure_loaded()
            system_content = ""
            user_content = ""
            for m in messages:
                if m.get("role") == "system" and m.get("content"):
                    system_content = m["content"]
                elif m.get("role") == "user" and m.get("content"):
                    user_content = m["content"]
            prompt = system_content if system_content else user_content
            # Flan-T5 max input ~512 tokens (~2000 chars). Was 512 chars - way too short.
            max_prompt_chars = 2000
            if len(prompt) > max_prompt_chars:
                # Keep start (instructions) + end (question + tail of context)
                head = prompt[: 800]
                tail = prompt[-(max_prompt_chars - 850) :]
                prompt = head + "\n...[truncated]...\n" + tail
            try:
                out = self._pipe(
                    prompt,
                    max_length=min(max_tokens, 256),
                    min_length=5,
                    num_return_sequences=1,
                    temperature=max(0.1, min(temperature, 1.0)),
                    do_sample=True,
                )
                text = (out[0]["generated_text"] if out else "").strip()
            except Exception as e:
                return f"[Error: {str(e)}]"
            return text if text else "[No response generated. Try a shorter question or different provider.]"

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _run)
        # Fix T5 tokenizer artifact (space between every character)
        result = _fix_t5_spaced_output(result)
        # Yield word-by-word for smoother streaming (model doesn't support true streaming)
        words = result.split()
        for w in words[:-1]:
            yield w + " "
        if words:
            yield words[-1]
