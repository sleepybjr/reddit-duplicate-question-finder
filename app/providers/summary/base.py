from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.models import AggregatedAnswer, PerSourceResult


class SummaryProvider(ABC):
    name: str = "base"

    @abstractmethod
    def summarize(
        self,
        question: Dict[str, Any],
        queries: Dict[str, Any],
        per_source_results: List[PerSourceResult],
        *,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> AggregatedAnswer:
        """
        Returns an AggregatedAnswer:
          - final_summary: str
          - per_source_results: the same list we received (or enriched)
        """
        raise NotImplementedError
