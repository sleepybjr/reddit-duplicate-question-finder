"""
Uses ArcticShift to retrieve top-level comments for a Reddit post.
"""

from typing import Any, Dict, List

import requests

ARCTIC_SHIFT_BASE = "https://arctic-shift.photon-reddit.com/api"


def build_comments_block(
    comments: List[Dict[str, Any]],
    link_fullname: str,
    top_n: int = 5,
) -> str:
    """
    Given a list of ArcticShift comments, build a bullet list of the top N top-level comments.
    """

    if not comments:
        return ""

    top_level = [
        c for c in comments
        if c.get("parent_id") == link_fullname
    ]

    top_level = [
        c for c in top_level
        if (c.get("body") or "").strip() not in ("", "[deleted]", "[removed]")
    ]

    if not top_level:
        return ""

    def score_of(c: Dict[str, Any]) -> int:
        return c.get("score", c.get("ups", 0))

    def sort_key(c: Dict[str, Any]):
        return (
            score_of(c),
            c.get("created_utc", 0),
        )

    top_level_sorted = sorted(top_level, key=sort_key, reverse=True)

    top_comments = top_level_sorted[:top_n]

    bullets = "\n".join(f"- {c.get('body', '').strip()}" for c in top_comments)

    return f"\n\nTop comments:\n{bullets}"


def fetch_top_level_comments(
    link_fullname: str,
    limit: int = 10,
) -> List[str]:
    """
    Gets the top-level comments for a given Reddit link.
    """

    params: dict[str, object] = {
        "limit": limit,
        "link_id": link_fullname,
    }

    resp = requests.get(
        f"{ARCTIC_SHIFT_BASE}/comments/search", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    comments = data.get("data", data)
    print(f"ArcticShift returned {len(comments)} comments.")
    
    if not isinstance(comments, list):
        comments = []

    return comments
