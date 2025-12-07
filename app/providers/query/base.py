from abc import ABC, abstractmethod
from typing import Dict, Any

from app.core.models import QuestionInput


class QueryProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate_queries(self, question: QuestionInput) -> Dict[str, Any]:
        """
        Given a QuestionInput, return a dict containing:
          - keyword_query or keyword_queries
          - sub_questions
          - any other provider-specific metadata
        """
        raise NotImplementedError
