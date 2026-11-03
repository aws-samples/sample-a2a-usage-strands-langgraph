"""Curated re:Invent 2026 session search for the OPN408 Strands agent.

This is intentionally a static, local JSON search rather than RAG. It gives the
Code Talk a reliable, inspectable tool call; embeddings and semantic retrieval
remain a future extension.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from strands import tool

CATALOG_PATH = Path(__file__).with_name("reinvent-2026-curated-sessions.json")
MAX_RESULTS = 5


def load_catalog() -> dict[str, Any]:
    """Load the versioned, static session snapshot shipped with the demo."""
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
    """Return deterministic, keyword-ranked session recommendations.

    Matching is deliberately transparent: title matches carry the highest weight,
    then topics/services, then summary text. The function never contacts a live
    catalog, so rehearsals remain stable and recommendation results are auditable.
    """
    if not query.strip():
        raise ValueError("A session recommendation query is required.")
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
        for _, session in sorted(
            ranked,
            key=lambda item: (-item[0], item[1]["sessionId"]),
        )[:limit]
    ]


@tool
def recommend_reinvent_sessions(query: str, limit: int = MAX_RESULTS) -> str:
    """Recommend up to five curated re:Invent 2026 sessions for an architecture question.

    Use this for questions about A2A, AgentCore, Strands, LangGraph, Bedrock,
    RAG, retrieval, observability, MCP, agent security, or production deployment.
    Explain that this is an unofficial static snapshot and attendees must verify
    schedule details in the official event catalog.
    """
    catalog = load_catalog()
    sessions = search_sessions(query, limit)
    result = {
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
    }
    return json.dumps(result, ensure_ascii=False)
