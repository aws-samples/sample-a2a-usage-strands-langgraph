from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "upgrade_agentcore_runtime_v2.py"
spec = importlib.util.spec_from_file_location("runtime_v2_upgrade", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
runtime_v2_upgrade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_v2_upgrade)


class RuntimeV2UpgradeTests(unittest.TestCase):
    def test_update_request_preserves_runtime_settings_and_selects_v2(self) -> None:
        runtime = {
            "agentRuntimeId": "sample-runtime-id",
            "agentRuntimeArtifact": {"codeConfiguration": {"code": {"s3": {"bucket": "sample", "prefix": "code.zip"}}}},
            "roleArn": "arn:example:role",
            "description": "sample",
            "environmentVariables": {"EXAMPLE": "value"},
            "protocolConfiguration": {"serverProtocol": "A2A"},
            "lifecycleConfiguration": {"idleRuntimeSessionTimeout": 900, "maxLifetime": 3600},
            "status": "READY",
        }

        request = runtime_v2_upgrade.build_v2_update_request(runtime)

        self.assertEqual(request["agentRuntimeId"], "sample-runtime-id")
        self.assertEqual(request["platformVersion"], "V2")
        self.assertEqual(request["environmentVariables"], {"EXAMPLE": "value"})
        self.assertEqual(request["protocolConfiguration"], {"serverProtocol": "A2A"})
        self.assertNotIn("status", request)


if __name__ == "__main__":
    unittest.main()
