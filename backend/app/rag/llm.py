"""Thin wrapper around a cloud-hosted LLM inference API (Groq).

Used by both the hybrid-RAG answer generation (Component 2/3) and the SQL RAG
NL<->SQL translation (Component 4), so both RAG paths share one place to
swap providers, add retries, logging, etc.

LLM_API_KEY is read from the environment / .env at runtime via
app.core.config.Settings - it is never hardcoded here or committed to the
repo (see .env.example).
"""
from functools import lru_cache

from groq import Groq

from app.core.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _get_client() -> Groq:
    return Groq(api_key=settings.llm_api_key)


def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
    reasoning_effort: str | None = None,
) -> str:
    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if reasoning_effort is not None:
        kwargs["reasoning_effort"] = reasoning_effort
    response = _get_client().chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return response.choices[0].message.content
