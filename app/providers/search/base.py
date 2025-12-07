from abc import ABC, abstractmethod
from typing import List
from app.core.models import PerSourceResult, QuestionInput


class SearchProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search(
        self,
        question: QuestionInput,
        keyword_queries: str,
    ) -> List[PerSourceResult]:
        """
        Returns a list of PerSourceResult
        """
        raise NotImplementedError
