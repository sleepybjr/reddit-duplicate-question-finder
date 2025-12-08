"""
Searches Reddit topics using a SearXNG instance, ranks them with Ollama,
and fetches top-level comments with ArcticShift.
"""
from typing import List, Optional
from urllib.parse import urlparse

import requests

from app.core.models import PerSourceResult, QuestionInput
from app.providers.comment_retrieval.arcticshift.comment_provider import (
    build_comments_block, fetch_top_level_comments)
from app.providers.search.base import SearchProvider
from app.providers.search.searxng.ollama_ranker import rerank_reddit_results

SEARXNG_BASE_URL = "http://localhost:8888"

class SearXNGSearchProvider(SearchProvider):
    name = "searxng"

    def search(self, question: QuestionInput, keyword_query: str) -> List[PerSourceResult]:
        results: List[PerSourceResult] = []

        try:
            resp = requests.get(
                f"{SEARXNG_BASE_URL}/search",
                params={
                    "q": keyword_query,
                    "format": "json",
                    "engines": "reddit",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            searx_results = data.get("results", [])
            
            print(f"SearXNG returned {len(searx_results)} searx_results results.")
            
            if not isinstance(searx_results, list):
                searx_results = []

            top_raw = rerank_reddit_results(
                question=question,
                raw_results=searx_results,
            )
            
            print(f"SearXNG returned {len(top_raw)} top_raw results.")

            for item in top_raw:
                url = item.get("url")
                topic_id = extract_reddit_topic_id(url or "")
                if topic_id:
                    link_fullname = reddit_post_id_to_fullname(topic_id)
                    comments = fetch_top_level_comments(link_fullname)

                    comments_block = build_comments_block(comments, link_fullname, top_n=5)

                    base_text = item.get("content") or item.get("title") or ""
                    summary_text = base_text + comments_block
                    
                    results.append(
                        PerSourceResult(
                            source="searxng:reddit",
                            url=url,
                            title=item.get("title"),
                            summary=summary_text,
                        )
                    )

        except Exception as e:
            results.append(
                PerSourceResult(
                    source="searxng",
                    url=None,
                    title="SearXNG search error",
                    summary=str(e),
                )
            )

        return results

def reddit_post_id_to_fullname(post_id: str) -> str:
    return f"t3_{post_id}"

def extract_reddit_topic_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path_parts = parsed.path.strip("/").split("/")

    if host.endswith("redd.it"):
        return path_parts[0] if path_parts else None

    if "reddit.com" in host:
        for i, part in enumerate(path_parts):
            if part == "comments" and i + 1 < len(path_parts):
                return path_parts[i + 1]

    return None
