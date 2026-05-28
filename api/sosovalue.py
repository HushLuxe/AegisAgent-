import os
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from backend.sosovalue_client import SoSoValueClient
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from backend.sosovalue_client import SoSoValueClient

import config.settings as settings


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_bits = urlparse(self.path)
        params = parse_qs(url_bits.query)

        try:
            client = SoSoValueClient()
            module = params.get("module", ["all"])[0]

            result = {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "sosovalue"}

            if module in ("all", "market"):
                market = client.get_market_overview(settings.SOSO_TRACKED_CURRENCIES[:5])
                result["market"] = [{
                    "id": s.get("_currency_id"),
                    "price": _sf(s.get("data", s).get("price", 0)),
                    "change_24h": _sf(s.get("data", s).get("priceChange24h", 0)),
                } for s in market]

            if module in ("all", "news"):
                news = client.get_full_news_feed(page_size=20)
                articles = client.extract_articles(news)
                sentiment = client.compute_news_sentiment(articles)
                result["news"] = {"count": len(articles), "sentiment": sentiment}

            if module in ("all", "macro"):
                result["macro"] = client.get_macro_impact()

            if module in ("all", "etf"):
                result["etf"] = client.get_etf_flow_signal()

            if module in ("all", "treasuries"):
                result["treasuries"] = client.get_btc_treasury_signal()

            if module in ("all", "indices"):
                indices = client.get_index_overview(settings.SOSO_TRACKED_INDICES)
                result["indices"] = [{
                    "ticker": i.get("_index_ticker"),
                    "price": _sf(i.get("data", i).get("price", 0)),
                    "change_24h": _sf(i.get("data", i).get("priceChange24h", 0)),
                } for i in indices]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, default=str).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


def _sf(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
