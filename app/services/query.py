"""
Loads and initializes the query provider based on configuration.
"""

from typing import Any, Dict

from app.core.config import get_default_query_provider
from app.core.models import QuestionInput
from app.providers.query.base import QueryProvider
from app.providers.query.ollama.query_provider import OllamaQueryProvider


def build_query_provider() -> QueryProvider:
    provider_name, provider_model = get_default_query_provider()

    if provider_name == "ollama_query":
        return OllamaQueryProvider(provider_model)

    raise ValueError(f"Unknown QUERY_PROVIDER: {provider_name}")


def generate_queries(question: QuestionInput) -> Dict[str, Any]:
    return _provider.generate_queries(question)


_provider = build_query_provider()
