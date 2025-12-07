"""
Loads and initializes the summary provider based on configuration.
"""

from typing import Any, Dict, List

from app.core.config import get_default_summary_provider
from app.core.models import AggregatedAnswer, PerSourceResult
from app.providers.summary.base import SummaryProvider
from app.providers.summary.ollama.summary_provider import OllamaSummaryProvider


def build_summary_provider() -> SummaryProvider:
    provider_name, provider_model = get_default_summary_provider()

    if provider_name == "ollama_summary":
        return OllamaSummaryProvider(provider_model)

    raise ValueError(f"Unknown SUMMARY_PROVIDER: {provider_name}")


def generate_summary(
    question: Dict[str, Any],
    queries: Dict[str, Any],
    per_source_results: List[PerSourceResult],
) -> AggregatedAnswer:
    return _provider.summarize(question=question, queries=queries, per_source_results=per_source_results)


_provider = build_summary_provider()
