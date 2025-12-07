"""
Main application entry point for the QA Retrieval Service.

Defines API endpoints for health checks, query generation, and searching with queries.
"""

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.models import AggregatedAnswer, PerSourceResult, QuestionInput
from app.services.query import generate_queries
from app.services.search import search_across_providers
from app.services.summary import generate_summary

app = FastAPI(
    title="Reddit Duplicate Question Service",
    description="Service that takes a question and returns historical answers",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate_queries")
def generate_queries_endpoint(question: QuestionInput):
    queries = generate_queries(question)
    print("Generated queries:", queries)
    return queries


@app.post("/generate_search", response_model=List[PerSourceResult])
def generate_search_endpoint(question: QuestionInput) -> List[PerSourceResult]:
    queries = generate_queries(question)
    print("Generated queries:", queries)

    per_source_results: List[PerSourceResult] = search_across_providers(
        question,
        queries.get("keyword_query", ""),
    )
    print("Returning search results:", len(per_source_results))

    return per_source_results


@app.post("/generate_summary", response_model=AggregatedAnswer)
def generate_summary_endpoint(question: QuestionInput) -> AggregatedAnswer:

    queries = generate_queries(question)
    print("Generated queries:", queries)

    # Whatever this returns, ensure it is List[PerSourceResult]
    per_source_results: List[PerSourceResult] = search_across_providers(
        question,
        queries.get("keyword_query", ""),
    )
    print("Returning search results:", len(per_source_results))

    question_dict = {
        "title": question.title,
        "body": question.body,
    }
    aggregated: AggregatedAnswer = generate_summary(
        question=question_dict,
        queries=queries,
        per_source_results=per_source_results,
    )
    print("Returning aggregated answer:", aggregated)

    return aggregated
