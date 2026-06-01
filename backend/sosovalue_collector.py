import json
import time
import logging
from datetime import datetime, timezone
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings
from backend.sosovalue_client import SoSoValueClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collect_sosovalue_data():
    """Collect full SoSoValue intelligence snapshot — news, market, macro, ETF, treasuries, indices."""
    client = SoSoValueClient()
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "sosovalue",
        "modules": {}
    }

    # 1. Market snapshots for tracked currencies
    logging.info("[SoSoValue] Collecting market snapshots...")
    
    # Build currency lookup map
    all_currencies = client.get_currencies()
    currency_map = {}
    for c in all_currencies.get("data", []):
        currency_map[c.get("currency_id")] = {
            "name": c.get("name", ""),
            "symbol": c.get("symbol", "").upper(),
        }
    
    market_data = client.get_market_overview(settings.SOSO_TRACKED_CURRENCIES)
    snapshot["modules"]["market"] = {
        "assets": [],
        "count": len(market_data),
    }
    for snap in market_data:
        cid = snap.get("_currency_id", "unknown")
        data = snap.get("data", snap)
        meta = currency_map.get(cid, {})
        snapshot["modules"]["market"]["assets"].append({
            "id": cid,
            "name": meta.get("name", data.get("name", cid)),
            "symbol": meta.get("symbol", data.get("symbol", cid[:4].upper())),
            "price": _sf(data.get("price", 0)),
            "change_24h": _sf(data.get("change_pct_24h", data.get("priceChange24h", 0))),
            "volume_24h": _sf(data.get("turnover_24h", data.get("volume24h", 0))),
            "market_cap": _sf(data.get("marketcap", data.get("marketCap", 0))),
        })
    logging.info(f"  -> {len(market_data)} assets collected")

    # 2. News feeds + sentiment
    logging.info("[SoSoValue] Collecting news feeds...")
    news_data = client.get_full_news_feed(page_size=50)
    articles = client.extract_articles(news_data)
    sentiment = client.compute_news_sentiment(articles)
    snapshot["modules"]["news"] = {
        "article_count": len(articles),
        "sentiment": sentiment,
        "articles": articles[:30],
    }
    logging.info(f"  -> {len(articles)} articles | Sentiment: {sentiment['label']} ({sentiment['score']:.0%})")

    # 3. Macro events
    logging.info("[SoSoValue] Collecting macro events...")
    macro = client.get_macro_impact()
    snapshot["modules"]["macro"] = macro
    logging.info(f"  -> Risk: {macro['risk_level']} | High-impact: {macro['high_impact_count']}")

    # 4. ETF flows
    logging.info("[SoSoValue] Collecting ETF data...")
    etf_signal = client.get_etf_flow_signal()
    snapshot["modules"]["etf"] = etf_signal
    logging.info(f"  -> ETF signal: {etf_signal['signal']} | Flow: {etf_signal['total_flow']:,.0f}")

    # 5. BTC Treasuries
    logging.info("[SoSoValue] Collecting BTC treasuries...")
    treasury = client.get_btc_treasury_signal()
    snapshot["modules"]["treasuries"] = treasury
    logging.info(f"  -> {treasury['company_count']} companies | {treasury['recent_buyers']} recent buyers")

    # 6. SoSoValue Indices
    logging.info("[SoSoValue] Collecting index data...")
    indices = client.get_index_overview(settings.SOSO_TRACKED_INDICES)
    snapshot["modules"]["indices"] = []
    for idx in indices:
        ticker = idx.get("_index_ticker", "unknown")
        data = idx.get("data", idx)
        snapshot["modules"]["indices"].append({
            "ticker": ticker,
            "name": data.get("name", ticker),
            "price": _sf(data.get("price", data.get("currentPrice", 0))),
            "change_24h": _sf(data.get("change_pct_24h", data.get("priceChange24h", 0))),
        })
    logging.info(f"  -> {len(indices)} indices collected")

    # 7. Sector spotlight
    logging.info("[SoSoValue] Collecting sector data...")
    sectors = client.get_sector_spotlight()
    snapshot["modules"]["sectors"] = sectors.get("data", sectors)
    logging.info(f"  -> Sector spotlight collected")

    # Save
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(raw_dir, f"sosovalue_{timestamp_str}.json")
    with open(filepath, 'w') as f:
        json.dump(snapshot, f, indent=2, default=str)

    # Also save as latest
    latest_path = os.path.join(raw_dir, "sosovalue_latest.json")
    with open(latest_path, 'w') as f:
        json.dump(snapshot, f, indent=2, default=str)

    logging.info(f"[SoSoValue] Snapshot saved: {filepath}")
    return snapshot


def _sf(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


if __name__ == "__main__":
    collect_sosovalue_data()
