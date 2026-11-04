"""Synthetic sample-catalog search for the optional Strands tool example.

This is a static local JSON search, not RAG. It demonstrates an inspectable tool
call; embeddings and semantic retrieval are intentionally out of scope.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from strands import tool

CATALOG_PATH = Path(__file__).with_name("sample-catalog.json")
MAX_RESULTS = 5


def load_catalog() -> dict[str, Any]:
    """Load the synthetic static catalog shipped with this sample."""
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.casefold()) if len(token) > 2}


def _searchable_text(session: dict[str, Any]) -> str:
    return " ".join(
        [
            session["title"],
            session["summary"],
            session["level"],
            session["type"],
            *session["topics"],
            *session["services"],
        ]
    ).casefold()


def search_sessions(query: str, limit: int = MAX_RESULTS) -> list[dict[str, Any]]:
    """Return deterministic keyword-ranked catalog entries.

    Title matches have the highest weight, followed by topic/service matches and
    then summary matches. The function never contacts a live service.
    """
    if not query.strip():
        raise ValueError("A catalog search query is required.")
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}.")

    query_tokens = _tokens(query)
    ranked: list[tuple[int, dict[str, Any]]] = []
    for session in load_catalog()["sessions"]:
        title = session["title"].casefold()
        topics_and_services = " ".join((*session["topics"], *session["services"])).casefold()
        searchable = _searchable_text(session)
        score = sum(
            5 if token in title else 3 if token in topics_and_services else 1
            for token in query_tokens
            if token in searchable
        )
        if score:
            ranked.append((score, session))

    return [
        session
        for _, session in sorted(ranked, key=lambda item: (-item[0], item[1]["sessionId"]))[:limit]
    ]


@tool
def recommend_catalog_items(query: str, limit: int = MAX_RESULTS) -> str:
    """Search a synthetic catalog for items relevant to an architecture question."""
    catalog = load_catalog()
    sessions = search_sessions(query, limit)
    return json.dumps(
        {
            "catalogSourceType": catalog["sourceType"],
            "catalogDisclaimer": catalog["disclaimer"],
            "query": query,
            "recommendations": [
                {
                    "sessionId": session["sessionId"],
                    "title": session["title"],
                    "summary": session["summary"],
                    "level": session["level"],
                    "type": session["type"],
                    "topics": session["topics"],
                }
                for session in sessions
            ],
        },
        ensure_ascii=False,
    )
