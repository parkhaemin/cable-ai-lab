"""Verify the function-call loop without a key or paid API call."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.agent import agent_live


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return SimpleNamespace(output=[
                SimpleNamespace(type="function_call", name="calculate_total",
                                call_id="call_demo", arguments='{"product_id":"T01","quantity":2}')
            ], output_text="")
        return SimpleNamespace(output=[], output_text="T01 두 개의 합계는 78,000원입니다.")


class LiveFlowTests(unittest.TestCase):
    def test_function_result_is_sent_back_to_model(self):
        fake = FakeResponses()
        with patch("app.agent.live_settings", return_value=("fake-key", "fake-model", "", "")):
            with patch("openai.OpenAI", return_value=SimpleNamespace(responses=fake)):
                result = agent_live("T01 2개 가격")
        self.assertEqual(len(fake.calls), 2)
        followup = fake.calls[1]["input"]
        self.assertEqual(followup[-1]["type"], "function_call_output")
        self.assertEqual(followup[-1]["call_id"], "call_demo")
        self.assertEqual(result["tool_trace"][0]["output"]["total"], 78000)


if __name__ == "__main__":
    unittest.main()
