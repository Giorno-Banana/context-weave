import json
import unittest

import httpx

from adaptive_evidence.planner import OpenAIPlanner, PlannedMemory, PlannerError
import test_contract as fixtures


class PlannerBoundaryTests(unittest.TestCase):
    def mock(self, value, finish="stop"):
        def handle(request):
            payload = json.loads(request.content)
            self.assertEqual("gpt-4o-mini", payload["model"])
            self.assertFalse(payload["store"])
            return httpx.Response(200, json={"choices": [{"finish_reason": finish,
                                                          "message": {"content": json.dumps(value)}}]})
        return OpenAIPlanner("fake-local-key", transport=httpx.MockTransport(handle))

    def test_unknown_source_is_rejected(self):
        planner = self.mock({"ids": ["other-user-secret"]})
        with self.assertRaises(PlannerError):
            planner.request("select", "Where?", [{"id": "allowed", "content": "Paris"}])

    def test_final_answer_field_is_rejected(self):
        planner = self.mock({"queries": [], "answer": "Paris"})
        with self.assertRaises(PlannerError):
            planner.request("expand", "Where?", [])

    def test_truncation_and_call_budget_fail_closed(self):
        planner = self.mock({"queries": []}, finish="length")
        with self.assertRaises(PlannerError):
            planner.request("expand", "Where?", [])
        planner.max_calls = planner.calls
        with self.assertRaises(PlannerError):
            planner.request("expand", "Where?", [])

    def test_bounded_json_queries_are_internal(self):
        planner = self.mock({"queries": ["Paris move", "Berlin move", "Paris move"]})
        self.assertEqual(["Paris move", "Berlin move"], planner.request("expand", "Where?", []))


def test_planned_sources(case):
    case.add(content="I moved from Paris to Berlin.")

    class Dummy:
        def request(self, stage, query, memories):
            if stage == "expand":
                return ["an invented statement that must never be returned"]
            return [memories[0]["id"]]

    result = PlannedMemory(case.store, Dummy()).search(user_id="u", query="List all cities", top_k=1)
    case.assertEqual(1, len(result))
    case.assertIn("I moved from Paris to Berlin.", result[0]["content"])
    case.assertNotIn("invented", str(result))


# Reuse fixture methods without inheriting/rerunning the contract tests.
PlannedEvidenceTests = type("PlannedEvidenceTests", (unittest.TestCase,), {
    "setUp": fixtures.ContractTests.setUp, "tearDown": fixtures.ContractTests.tearDown,
    "add": fixtures.ContractTests.add, "test_returns_only_ingested_sources": test_planned_sources})
