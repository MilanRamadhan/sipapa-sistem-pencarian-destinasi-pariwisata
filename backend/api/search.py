from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

# misal kamu punya fungsi search di file lain:
# from search_engine import search_query

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        q = params.get("q", [""])[0]

        # TODO: panggil fungsi search asli kamu di sini
        # results = search_query(q)
        results = [{"title": "Dummy", "url": "#", "score": 1.0}]  # ganti nanti

        body = json.dumps(results).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
        return
