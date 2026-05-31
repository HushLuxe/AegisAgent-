import time
import requests
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SoSoValueClient:
    """SoSoValue API client — covers all 9 data modules."""

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.SOSO_API_KEY
        self.base_url = settings.SOSO_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "x-soso-api-key": self.api_key,
            "Accept": "application/json",
        })

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.warning(f"SoSoValue API error {path}: {e}")
            return {"error": str(e), "path": path}

    # ── Currency & Pairs ──────────────────────────────────────

    def get_currencies(self):
        return self._get("/currencies")

    def get_currency_detail(self, currency_id):
        return self._get(f"/currencies/{currency_id}")

    def get_currency_snapshot(self, currency_id):
        return self._get(f"/currencies/{currency_id}/market-snapshot")

    def get_currency_klines(self, currency_id, interval="1d", start=None, end=None):
        params = {"interval": interval}
        if start: params["start"] = start
        if end: params["end"] = end
        return self._get(f"/currencies/{currency_id}/klines", params)

    def get_currency_supply(self, currency_id):
        return self._get(f"/currencies/{currency_id}/supply")

    def get_currency_pairs(self, currency_id):
        return self._get(f"/currencies/{currency_id}/pairs")

    def get_sector_spotlight(self):
        return self._get("/currencies/sector-spotlight")

    def get_currency_fundraising(self, currency_id):
        return self._get(f"/currencies/{currency_id}/fundraising")

    # ── ETF ───────────────────────────────────────────────────

    def get_etf_summary_history(self):
        return self._get("/etfs/summary-history")

    def get_etf_list(self):
        return self._get("/etfs")

    def get_etf_snapshot(self, ticker):
        return self._get(f"/etfs/{ticker}/market-snapshot")

    def get_etf_history(self, ticker):
        return self._get(f"/etfs/{ticker}/history")

    # ── SoSoValue Index ──────────────────────────────────────

    def get_indices(self):
        return self._get("/indices")

    def get_index_constituents(self, index_ticker):
        return self._get(f"/indices/{index_ticker}/constituents")

    def get_index_snapshot(self, index_ticker):
        return self._get(f"/indices/{index_ticker}/market-snapshot")

    def get_index_klines(self, index_ticker, interval="1d"):
        return self._get(f"/indices/{index_ticker}/klines", {"interval": interval})

    # ── Crypto Stocks ────────────────────────────────────────

    def get_crypto_stocks(self):
        return self._get("/crypto-stocks")

    def get_stock_snapshot(self, stock_ticker):
        return self._get(f"/crypto-stocks/{stock_ticker}/market-snapshot")

    def get_stock_market_cap(self, stock_ticker):
        return self._get(f"/crypto-stocks/{stock_ticker}/market-cap")

    def get_stock_klines(self, stock_ticker, interval="1d"):
        return self._get(f"/crypto-stocks/{stock_ticker}/klines", {"interval": interval})

    def get_stock_sectors(self):
        return self._get("/crypto-stocks/sector")

    def get_sector_index(self, sector_name):
        return self._get(f"/crypto-stocks/sector/{sector_name}/index")

    # ── BTC Treasuries ───────────────────────────────────────

    def get_btc_treasuries(self):
        return self._get("/btc-treasuries")

    def get_btc_purchase_history(self, ticker):
        return self._get(f"/btc-treasuries/{ticker}/purchase-history")

    # ── Feeds (News) ─────────────────────────────────────────

    def get_news(self, page=1, page_size=20):
        return self._get("/news", {"page": page, "pageSize": page_size})

    def get_hot_news(self):
        return self._get("/news/hot")

    def get_featured_news(self):
        return self._get("/news/featured")

    def search_news(self, keyword, page=1, page_size=20):
        return self._get("/news/search", {"keyword": keyword, "page": page, "pageSize": page_size})

    # ── Fundraising ──────────────────────────────────────────

    def get_fundraising_projects(self, page=1, page_size=20):
        return self._get("/fundraising/projects", {"page": page, "pageSize": page_size})

    def get_fundraising_detail(self, project_id):
        return self._get(f"/fundraising/projects/{project_id}")

    # ── Macro ────────────────────────────────────────────────

    def get_macro_events(self, date):
        return self._get("/macro/events", {"date": date})

    def get_macro_event_history(self, event):
        return self._get(f"/macro/events/{event}/history")

    # ── Analysis Charts ──────────────────────────────────────

    def get_analysis_charts(self):
        return self._get("/analyses")

    def get_analysis_chart_data(self, chart_name):
        return self._get(f"/analyses/{chart_name}")

    # ── Batch Helpers ────────────────────────────────────────

    def get_market_overview(self, currency_ids):
        snapshots = []
        for cid in currency_ids:
            snap = self.get_currency_snapshot(cid)
            if "error" not in snap:
                snap["_currency_id"] = cid
                snapshots.append(snap)
            time.sleep(settings.SOSO_DELAY)
        return snapshots

    def get_full_news_feed(self, page_size=50):
        news = self.get_news(page_size=page_size)
        hot = self.get_hot_news()
        featured = self.get_featured_news()
        return {"news": news, "hot": hot, "featured": featured, "fetched_at": int(time.time() * 1000)}

    def get_index_overview(self, tickers):
        results = []
        for ticker in tickers:
            snap = self.get_index_snapshot(ticker)
            if "error" not in snap:
                snap["_index_ticker"] = ticker
                results.append(snap)
            time.sleep(settings.SOSO_DELAY)
        return results

    def get_etf_flow_signal(self):
        summary = self.get_etf_summary_history()
        data = summary.get("data", summary)
        if isinstance(data, list) and data:
            latest = data[-1]
            total_flow = self._safe_float(latest.get("totalNetFlow", latest.get("net_flow", 0)))
        elif isinstance(data, dict):
            total_flow = self._safe_float(data.get("totalNetFlow", data.get("net_flow", 0)))
        else:
            total_flow = 0

        if total_flow > 100_000_000:
            return {"signal": "strong_inflow", "score": 0.9, "total_flow": total_flow}
        elif total_flow > 10_000_000:
            return {"signal": "inflow", "score": 0.7, "total_flow": total_flow}
        elif total_flow < -100_000_000:
            return {"signal": "strong_outflow", "score": 0.1, "total_flow": total_flow}
        elif total_flow < -10_000_000:
            return {"signal": "outflow", "score": 0.3, "total_flow": total_flow}
        return {"signal": "neutral", "score": 0.5, "total_flow": total_flow}

    def get_btc_treasury_signal(self):
        treasuries = self.get_btc_treasuries()
        data = treasuries.get("data", treasuries)
        items = data if isinstance(data, list) else data.get("list", []) if isinstance(data, dict) else []
        total_btc = sum(self._safe_float(t.get("totalBtc", t.get("btc_amount", 0))) for t in items)
        recent_buyers = sum(1 for t in items if self._safe_float(t.get("recentChange", t.get("change", 0))) > 0)
        return {
            "total_btc_held": total_btc,
            "company_count": len(items),
            "recent_buyers": recent_buyers,
            "concentration": "diversified" if len(items) > 10 else "concentrated",
            "sentiment": "bullish" if recent_buyers > len(items) * 0.5 else "neutral",
        }

    def compute_news_sentiment(self, articles):
        positive_kw = ["surge", "rally", "bullish", "breakout", "adoption", "partnership",
                       "approval", "launch", "upgrade", "growth", "record", "high", "accumulation"]
        negative_kw = ["crash", "dump", "bearish", "hack", "exploit", "ban", "regulation",
                       "sec", "lawsuit", "fraud", "scam", "sell-off", "decline", "liquidation"]
        pos, neg = 0, 0
        for a in articles:
            text = ((a.get("title", "") or "") + " " + (a.get("description", "") or a.get("summary", "") or "")).lower()
            if any(kw in text for kw in positive_kw): pos += 1
            if any(kw in text for kw in negative_kw): neg += 1
        total = len(articles)
        score = pos / total if total > 0 else 0.5
        label = "bullish" if score > 0.6 else "bearish" if score < 0.3 else "neutral"
        return {"score": round(score, 3), "label": label, "positive": pos, "negative": neg, "total": total}

    def get_macro_impact(self, date=None):
        from datetime import datetime, timezone
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        result = self.get_macro_events(date)
        data = result.get("data", result)
        events = data if isinstance(data, list) else data.get("events", data.get("list", [])) if isinstance(data, dict) else []
        high = [e for e in events if str(e.get("impact", "")).lower() in ("high", "3")]
        medium = [e for e in events if str(e.get("impact", "")).lower() in ("medium", "2")]
        return {
            "high_impact_count": len(high),
            "medium_impact_count": len(medium),
            "high_impact_events": high[:5],
            "risk_level": "high" if len(high) >= 3 else "medium" if len(high) >= 1 else "low",
        }

    def extract_articles(self, news_data):
        articles = []
        for key in ("news", "hot", "featured"):
            feed = news_data.get(key, {})
            data = feed.get("data", feed)
            if isinstance(data, list):
                articles.extend(data)
            elif isinstance(data, dict):
                articles.extend(data.get("list", data.get("items", [])))
        seen, unique = set(), []
        for a in articles:
            title = a.get("title", "")
            if title and title not in seen:
                seen.add(title)
                unique.append(a)
        return unique

    @staticmethod
    def _safe_float(val, default=0.0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default
