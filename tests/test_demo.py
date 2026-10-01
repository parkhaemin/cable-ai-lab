"""Focused checks of the no-key learning path."""
import unittest
from app.agent import calculate_total, agent_demo
from app.data import load_documents
from app.rag import answer_question
from app.search import search_demo


class DemoTests(unittest.TestCase):
    def test_source_and_extractive_answer(self):
        result = answer_question("상품 문의는 어디에서 하나요?")
        self.assertEqual(result["sources"][0]["id"], "faq-contact")
        self.assertIn("[faq-contact]", result["answer"])
        self.assertFalse(result["generated"])

    def test_quantity_and_stock_validation(self):
        self.assertEqual(calculate_total("T01", 2)["total"], 78000)
        self.assertIn("error", calculate_total("T01", 99))

    def test_agent_tool_trace(self):
        result = agent_demo("T01 2개 가격은 얼마인가요?")
        self.assertEqual(result["tool_trace"][-1]["tool"], "calculate_total")
        self.assertIn("78,000원", result["answer"])

    def test_retrieval_records_document_ids(self):
        ids = {d["id"] for d in load_documents()}
        self.assertTrue(all(hit["id"] in ids for hit in search_demo("배송")))


if __name__ == "__main__":
    unittest.main()
