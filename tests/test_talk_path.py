from __future__ import annotations

import unittest

from starlette.testclient import TestClient

from talk.langgraph_researcher import PROFILE, streaming_request
from talk.strands_analyst import build_app


class TalkPathTests(unittest.TestCase):
    def test_rehearsal_server_publishes_a_real_a2a_agent_card(self) -> None:
        with TestClient(build_app(model_mode="rehearsal")) as client:
            response = client.get("/.well-known/agent-card.json")

        self.assertEqual(response.status_code, 200)
        card = response.json()
        self.assertEqual(card["name"], "Strands A2A Specialist")
        self.assertTrue(card["capabilities"]["streaming"])
        self.assertEqual(card["skills"][0]["id"], "design-knowledge-catalog-architecture")

    def test_resumed_request_preserves_task_and_context_identity(self) -> None:
        request = streaming_request(PROFILE, task_id="task-1", context_id="context-1")

        self.assertEqual(request.params.message.task_id, "task-1")
        self.assertEqual(request.params.message.context_id, "context-1")
        self.assertEqual(request.params.message.parts[0].model_dump()["text"], PROFILE)


if __name__ == "__main__":
    unittest.main()
