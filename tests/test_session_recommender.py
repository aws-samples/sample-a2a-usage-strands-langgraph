from __future__ import annotations

import json
import unittest

from talk.session_recommender_tool import recommend_reinvent_sessions, search_sessions


class SessionRecommenderTests(unittest.TestCase):
    def test_a2a_query_surfaces_a2a_and_agentcore_sessions(self) -> None:
        results = search_sessions("A2A AgentCore multi-agent architecture")

        self.assertTrue(results)
        self.assertTrue(any("A2A" in " ".join(session["topics"]) for session in results))
        self.assertTrue(any("AgentCore" in session["summary"] or "AgentCore" in session["title"] for session in results))

    def test_tool_returns_static_catalog_disclaimer_and_capped_results(self) -> None:
        payload = json.loads(recommend_reinvent_sessions("Strands LangGraph production agents", 5))

        self.assertIn("Unofficial", payload["catalogSourceType"])
        self.assertLessEqual(len(payload["recommendations"]), 5)
        self.assertTrue(any("Strands" in session["summary"] or "Strands" in session["title"] for session in payload["recommendations"]))

    def test_tool_rejects_empty_query_and_large_limit(self) -> None:
        with self.assertRaises(ValueError):
            search_sessions("", 3)
        with self.assertRaises(ValueError):
            search_sessions("AgentCore", 6)


if __name__ == "__main__":
    unittest.main()
