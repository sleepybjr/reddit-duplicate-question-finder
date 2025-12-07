"""
Uses Ollama LLM to generate search queries based on a given question.
"""
import json
from typing import Any, Dict

from ollama import chat

from app.core.models import QuestionInput
from app.core.template_loader import load_template
from app.providers.query.base import QueryProvider


class OllamaQueryProvider(QueryProvider):
    name = "ollama_llm"

    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name
        self.prompt_template = load_template("llm_query_prompt.txt")

    def generate_queries(self, question: QuestionInput) -> Dict[str, Any]:
        user_text = (
            f"Title: {question.title}\n"
            f"Body: {question.body or ''}\n"
            f"Source: {question.source or ''}\n"
            f"URL: {question.url or ''}"
        )

        response = chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": user_text},
            ],
        )

        content = response["message"]["content"]
        try:
            return json.loads(content)
        except Exception:
            return {
                "keyword_queries": [question.title],
                "sub_questions": []
            }
