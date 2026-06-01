"""Tests for the deterministic output compressor and the MCP handlers."""

import unittest

from monolith.mcp_server import handle_request
from monolith.shrink import shrink


class ShrinkTests(unittest.TestCase):
    def test_collapses_blank_runs(self):
        result = shrink("a\n\n\n\n\nb", "lite")
        self.assertEqual(result.text, "a\n\nb")

    def test_strips_trailing_whitespace(self):
        result = shrink("line   \n", "lite")
        self.assertEqual(result.text, "line")

    def test_full_folds_identical_lines_and_strips_ansi(self):
        text = "\x1b[31mERR\x1b[0m\n" + "same\n" * 4
        result = shrink(text, "full")
        self.assertNotIn("\x1b[", result.text)
        self.assertIn("(x4)", result.text)
        self.assertLess(result.after_tokens, result.before_tokens)

    def test_ultra_clips_long_output(self):
        text = "\n".join(f"line {i}" for i in range(500))
        result = shrink(text, "ultra")
        self.assertIn("omitted", result.text)
        self.assertLess(result.after_tokens, result.before_tokens)

    def test_unknown_level_raises(self):
        with self.assertRaises(ValueError):
            shrink("x", "nope")


class McpHandlerTests(unittest.TestCase):
    def test_initialize_reports_server_info(self):
        resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(resp["result"]["serverInfo"]["name"], "monolith-shrink")

    def test_tools_list_exposes_shrink(self):
        resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = [t["name"] for t in resp["result"]["tools"]]
        self.assertEqual(names, ["shrink"])

    def test_tools_call_compresses(self):
        resp = handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "shrink", "arguments": {"text": "a\n\n\n\nb", "level": "lite"}},
        })
        self.assertEqual(resp["result"]["content"][0]["text"], "a\n\nb")
        self.assertIn("reduction", resp["result"]["_meta"])

    def test_unknown_method_errors(self):
        resp = handle_request({"jsonrpc": "2.0", "id": 4, "method": "bogus"})
        self.assertEqual(resp["error"]["code"], -32601)

    def test_notification_gets_no_response(self):
        self.assertIsNone(handle_request({"jsonrpc": "2.0", "method": "initialized"}))


if __name__ == "__main__":
    unittest.main()
