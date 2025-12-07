"""
Data models for question input and aggregated answers.
"""

from pydantic import BaseModel
from typing import Optional, List

class QuestionInput(BaseModel):
    """
    Data model for question input.
    """
    title: str
    body: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None


class PerSourceResult(BaseModel):
    """
    Data model for results from individual sources.
    """
    source: str
    url: Optional[str] = None
    title: Optional[str] = None
    summary: str

class AggregatedAnswer(BaseModel):
    """
    Data model for the aggregated answer.
    """
    final_summary: str
    per_source_results: List[PerSourceResult]
