"""
Provides a summary provider implementation using the Ollama LLM.
"""
import json
import os
from typing import Any, Dict, List, Optional

import ollama

from app.core.models import AggregatedAnswer, PerSourceResult
from app.core.template_loader import load_template
from app.providers.summary.base import SummaryProvider


class OllamaSummaryProvider(SummaryProvider):
    name = "ollama_llm"

    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name or os.getenv("SUMMARY_MODEL", "llama3.1")
        self.prompt_template = load_template("llm_summary_prompt.txt")

    def summarize(
        self,
        question: Dict[str, Any],
        queries: Dict[str, Any],
        per_source_results: List[PerSourceResult],
        *,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> AggregatedAnswer:
        all_texts: List[str] = []

        for src in per_source_results:
            header_parts: List[str] = []
            if src.title:
                header_parts.append(src.title)
            if src.url:
                header_parts.append(f"({src.url})")

            header = " ".join(header_parts) if header_parts else src.source
            evidence_line = f"{header}: {src.summary}"

            all_texts.append(f"[{src.source}] {evidence_line}")

        combined_text = "\n".join(all_texts)

        if not combined_text.strip():
            combined_text = "No detailed results were available to summarize."

        title = question.get("title", "")
        body = question.get("body", "")

        template_values = {
            "question_title": title,
            "question_body": body,
            "generated_queries": json.dumps(queries, indent=2),
            "combined_evidence": combined_text,
        }

        prompt = self.prompt_template.format(**template_values)

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response["message"]["content"]

        return AggregatedAnswer(
            final_summary=content,
            per_source_results=per_source_results,
        )

    def _extract_text(self, item: Any) -> str:
        if hasattr(item, "text"):
            return str(item.text)
        if hasattr(item, "snippet"):
            return str(item.snippet)
        if hasattr(item, "title") and hasattr(item, "url"):
            return f"{item.title} ({item.url})"

        if isinstance(item, dict):
            if "text" in item:
                return str(item["text"])
            if "snippet" in item:
                return str(item["snippet"])
            if "title" in item and "url" in item:
                return f"{item['title']} ({item['url']})"
            return str(item)

        return str(item)
