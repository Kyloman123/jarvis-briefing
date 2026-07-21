#!/usr/bin/env python3
import csv
import json
import pathlib
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


ROOT = pathlib.Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/stocks":
            self.handle_stocks(parsed)
            return
        super().do_GET()

    def handle_stocks(self, parsed):
        params = urllib.parse.parse_qs(parsed.query)
        symbols = params.get("symbols", [""])[0]
        clean_symbols = [
            symbol.strip().upper()
            for symbol in symbols.split(",")
            if symbol.strip()
        ]
        if not clean_symbols:
            self.send_json({"error": "No symbols provided"}, status=400)
            return

        try:
            stocks = []
            for symbol in clean_symbols:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range=5d&interval=1d"
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=12) as response:
                    payload = json.loads(response.read().decode("utf-8", errors="replace"))
                result = (payload.get("chart", {}).get("result") or [{}])[0]
                meta = result.get("meta", {})
                quote = ((result.get("indicators", {}).get("quote") or [{}])[0])
                closes = [
                    value for value in quote.get("close", [])
                    if isinstance(value, (int, float))
                ]
                current = meta.get("regularMarketPrice")
                previous = meta.get("previousClose")
                if current is None and closes:
                    current = closes[-1]
                if previous is None and len(closes) > 1:
                    previous = closes[-2]
                change_pct = 0
                if current is not None and previous:
                    change_pct = ((current - previous) / previous) * 100
                updated = ""
                if meta.get("regularMarketTime"):
                    updated = time.strftime(
                        "%Y-%m-%d %H:%M",
                        time.localtime(meta["regularMarketTime"])
                    )
                stocks.append({
                    "symbol": meta.get("symbol", symbol).upper(),
                    "name": meta.get("longName") or meta.get("shortName") or symbol.upper(),
                    "price": f"{current:.2f}" if isinstance(current, (int, float)) else "N/A",
                    "change": f"{change_pct:+.2f}%",
                    "updated": updated,
                })
            self.send_json({"stocks": stocks})
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=502)

    def send_json(self, payload, status=200):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    port = 8765
    print(f"Jarvis Briefing running at http://127.0.0.1:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
