"""
Generates answers using an Ollama LLM model based on the provided question and keyword queries.
"""
from typing import List

from ollama import chat

from app.core.models import PerSourceResult, QuestionInput
from app.core.template_loader import load_template
from app.providers.search.base import SearchProvider


class OllamaLlmSearchProvider(SearchProvider):
    name = "ollama_llm"

    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name
        self.prompt_template = load_template("llm_search_prompt.txt")

    def search(self, question: QuestionInput, keyword_queries: str) -> List[PerSourceResult]:
        user_content = (
            f"Title: {question.title}\n"
            f"Body: {question.body or ''}\n\n"
            f"Keyword queries:\n{keyword_queries}\n\n"
            "Answer this question as best as you can based on your own knowledge."
        )

        resp = chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": user_content},
            ],
        )

        answer = resp["message"]["content"]

        return [
            PerSourceResult(
                source="llm:ollama",
                url=None,
                title="LLM internal answer",
                summary=answer,
            )
        ]
