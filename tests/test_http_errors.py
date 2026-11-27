"""Offline tests for error results and timeouts, against a local stub server."""

import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from databunkerpro import DatabunkerproAPI

# endpoint -> (HTTP status, body, delay in seconds)
REPLIES = {
    "UserGet": (
        404,
        {"status": "error", "message": "The user record was not found"},
        0,
    ),
    "UserCreate": (409, {"status": "error", "message": "Duplicate index: login"}, 0),
    "FileGet": (502, "<html>Bad Gateway</html>", 0),
    "TokenGet": (500, {"message": "boom"}, 0),
    "SystemGetSystemStats": (200, {"status": "ok", "stats": {}}, 0),
    "Slow": (200, {"status": "ok"}, 2),
}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        code, body, delay = REPLIES[self.path.rsplit("/", 1)[-1]]
        time.sleep(delay)
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except OSError:
            pass  # the client gave up (timeout test)

    def log_message(self, *args):
        pass


class TestHttpErrors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.api = DatabunkerproAPI(cls.url, "TOKEN")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_error_keeps_server_message_and_adds_httpcode(self):
        self.assertEqual(
            self.api.get_user("login", "x"),
            {
                "status": "error",
                "message": "The user record was not found",
                "httpcode": 404,
            },
        )
        self.assertEqual(self.api.create_user({"login": "x"})["httpcode"], 409)

    def test_error_without_status_field(self):
        self.assertEqual(
            self.api.get_token("t"),
            {"status": "error", "message": "boom", "httpcode": 500},
        )

    def test_non_json_reply(self):
        result = self.api.get_file("login", "x", filename="f")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["httpcode"], 502)

    def test_success_has_no_httpcode(self):
        self.assertEqual(self.api.get_system_stats(), {"status": "ok", "stats": {}})

    def test_connection_failure_has_no_httpcode(self):
        api = DatabunkerproAPI("http://127.0.0.1:9", "TOKEN", timeout=2)
        result = api.get_user("login", "x")
        self.assertEqual(result["status"], "error")
        self.assertNotIn("httpcode", result)

    def test_timeout_returns_error(self):
        api = DatabunkerproAPI(self.url, "TOKEN", timeout=0.5)
        start = time.monotonic()
        result = api._make_request("Slow")
        self.assertLess(time.monotonic() - start, 1.5)
        self.assertEqual(result["status"], "error")
        self.assertIn("timed out", result["message"].lower())

    def test_raw_request_timeout_raises(self):
        api = DatabunkerproAPI(self.url, "TOKEN", timeout=0.5)
        with self.assertRaises(requests.exceptions.Timeout):
            api.raw_request("Slow")

    def test_default_timeout(self):
        self.assertEqual(self.api.timeout, (10.0, 300.0))
        self.assertIsNone(DatabunkerproAPI(self.url, timeout=None).timeout)
