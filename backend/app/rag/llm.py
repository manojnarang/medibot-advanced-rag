"""Thin wrapper around a cloud-hosted LLM inference API.

Used by both the hybrid-RAG answer generation (Component 2/3) and the SQL RAG
NL<->SQL translation (Component 4). Fill this in with, e.g., the Anthropic
SDK, using LLM_PROVIDER / LLM_API_KEY / LLM_MODEL from app.core.config.

Keeping this as a single seam means both RAG paths share one place to swap
providers, add retries, logging, etc.
"""
from app.core.config import get_settings

settings = get_settings()


def generate(system_prompt: str, user_prompt: str) -> str:
    """TODO: call the configured cloud LLM (e.g. Anthropic Messages API) and
    return its text response.

    Example (once the `anthropic` package is installed and LLM_API_KEY set):

        import anthropic
        client = anthropic.Anthropic(api_key=settings.llm_api_key)
        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
    """
    raise NotImplementedError(
        "Wire up app.rag.llm.generate() to your cloud LLM provider "
        f"(configured provider: {settings.llm_provider}, model: {settings.llm_model})."
    )
