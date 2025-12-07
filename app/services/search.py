"""
Loads and initializes the search providers based on configuration.
"""

from typing import List

from app.core.config import get_default_search_providers
from app.core.models import PerSourceResult, QuestionInput
from app.providers.search.base import SearchProvider
from app.providers.search.ollama.search_provider import OllamaLlmSearchProvider
from app.providers.search.searxng.search_provider import SearXNGSearchProvider


def build_search_providers() -> List[SearchProvider]:
    providers = get_default_search_providers()
    search_providers: List[SearchProvider] = []

    for provider_name, provider_model in providers:
        if provider_name == "ollama_search":
            search_providers.append(OllamaLlmSearchProvider(provider_model))
        elif provider_name == "searxng":
            search_providers.append(SearXNGSearchProvider())
        else:
            raise ValueError(f"Unknown SEARCH_PROVIDER: {provider_name}")

    return search_providers


def search_across_providers(question: QuestionInput, keyword_queries: str) -> List[PerSourceResult]:
    all_results: List[PerSourceResult] = []
    for search_provider in _providers:
        all_results.extend(search_provider.search(question, keyword_queries))

    print(f"Total results from all providers: {len(all_results)}")
    return all_results


_providers = build_search_providers()
