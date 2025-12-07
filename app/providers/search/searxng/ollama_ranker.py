"""
Uses Ollama LLM to rerank Reddit search results from SearXNG.
"""

import json
from typing import Any, Dict, List

from ollama import chat

from app.core.models import QuestionInput
from app.core.template_loader import load_template

MODEL_NAME = "llama3.1"  # or whatever you use in your project


def rerank_reddit_results(
    question: QuestionInput,
    raw_results: List[Dict[str, Any]],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    if not raw_results:
        return []

    question_text = question.title
    if getattr(question, "body", None):
        question_text += "\n\n" + question.body

    items_text_lines = []
    for i, item in enumerate(raw_results):
        title = item.get("title") or ""
        snippet = item.get("content") or ""
        url = item.get("url") or ""
        items_text_lines.append(
            f"{i+1}. Title: {title}\n"
            f"   Snippet: {snippet}\n"
            f"   URL: {url}"
        )
    items_text = "\n\n".join(items_text_lines)

    template = load_template("reddit_rerank_prompt.txt")

    prompt = template.format(
        question_text=question_text,
        items_text=items_text,
        top_k=top_k,
    )

    resp = chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "top_p": 1,
            "top_k": 0,
            "seed": 42,
        },
    )

    text = resp["message"]["content"].strip()

    try:
        indices = json.loads(text)
        if not isinstance(indices, list):
            raise ValueError("reranker did not return a list")
    except Exception:
        return raw_results[:top_k]

    print(f"Reranker selected indices: {indices}")

    chosen = []
    for idx in indices:
        if not isinstance(idx, int):
            continue
        pos = idx - 1
        if 0 <= pos < len(raw_results):
            chosen.append(raw_results[pos])
        if len(chosen) >= top_k:
            break

    if not chosen:
        return raw_results[:top_k]

    return chosen
