import json
import time
import requests
import logging
from datetime import datetime, timezone
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DELAY_BETWEEN_TOKENS = 3
GECKOTERMINAL_BASE_URL = "https://api.geckoterminal.com/api/v2"
TRENDING_TOKENS_LIMIT = int(os.environ.get("TRENDING_TOKENS_LIMIT", "12"))
TRENDING_DURATION = os.environ.get("TRENDING_DURATION", "24h")
MIN_TRENDING_TOKENS = int(os.environ.get("MIN_TRENDING_TOKENS", "4"))
MIN_TOKENS = int(os.environ.get("MIN_TOKENS", "10"))
TRENDING_CACHE_PATH = os.environ.get(
    "TRENDING_CACHE_PATH",
    os.path.join(BASE_DIR, "data", "cache", "trending_tokens.json")
)

SYMBOL_FALLBACK = {
    "0x02de4766c272abc10bc88c220d214a26960a7e53": "CELO-V1-LP",
    "0x471ece3750da237f93b8e339c536989b8978a438": "cWETH",
}

def fetch_dexscreener(address):
    try:
        response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}", timeout=10)
        time.sleep(settings.DEXSCREENER_DELAY)
        if response.status_code == 200:
            pairs = response.json().get("pairs", [])
            if pairs:
                return max(pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0))
    except Exception as e:
        logging.warning(f"Error fetching DexScreener for {address}: {e}")
    return {}

def fetch_geckoterminal_ohlcv(address):
    try:
        dex_res = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}", timeout=10)
        time.sleep(settings.DEXSCREENER_DELAY)
        pairs = dex_res.json().get("pairs", [])
        if not pairs:
            return []
        pool_address = pairs[0].get("pairAddress")
        url = f"https://api.geckoterminal.com/api/v2/networks/celo/pools/{pool_address}/ohlcv/hour?limit=24"
        response = requests.get(url, timeout=10)
        time.sleep(settings.GECKOTERMINAL_DELAY)
        if response.status_code == 200:
            return response.json().get("data", {}).get("attributes", {}).get("ohlcv_list", [])
    except Exception as e:
        logging.warning(f"Error fetching GeckoTerminal for {address}: {e}")
    return []

def _parse_geckoterminal_token_id(token_id, network):
    if not token_id:
        return None
    if token_id.startswith(f"{network}_"):
        return token_id.split("_", 1)[1]
    if ":" in token_id:
        prefix, raw = token_id.split(":", 1)
        if prefix == network:
            return raw
    return token_id

def fetch_trending_tokens(network, limit=TRENDING_TOKENS_LIMIT, duration=TRENDING_DURATION):
    url = (
        f"{GECKOTERMINAL_BASE_URL}/networks/{network}/trending_pools"
        f"?include=base_token,quote_token&page=1&duration={duration}"
    )
    try:
        response = requests.get(url, timeout=10, headers={"accept": "application/json"})
        time.sleep(settings.GECKOTERMINAL_DELAY)
        if response.status_code != 200:
            logging.warning(f"GeckoTerminal trending pools failed: {response.status_code}")
            return []
        payload = response.json()
    except Exception as e:
        logging.warning(f"Error fetching GeckoTerminal trending pools: {e}")
        return []

    token_id_to_addr = {}
    for item in payload.get("included", []):
        if item.get("type") != "token":
            continue
        token_id = item.get("id")
        attrs = item.get("attributes", {})
        addr = attrs.get("address") or attrs.get("token_address")
        if not addr and token_id:
            addr = _parse_geckoterminal_token_id(token_id, network)
        if token_id and addr:
            token_id_to_addr[token_id] = addr

    tokens = []
    seen = set()

    def add_token(addr):
        if not addr:
            return
        normalized = addr.lower()
        if normalized in seen:
            return
        seen.add(normalized)
        tokens.append(normalized)

    for pool in payload.get("data", []):
        relationships = pool.get("relationships", {})
        for key in ("base_token", "quote_token"):
            rel_data = relationships.get(key, {}).get("data")
            token_id = rel_data.get("id") if isinstance(rel_data, dict) else None
            addr = token_id_to_addr.get(token_id) if token_id else None
            if not addr and token_id:
                addr = _parse_geckoterminal_token_id(token_id, network)
            add_token(addr)
            if len(tokens) >= limit:
                break
        if len(tokens) >= limit:
            break

    return tokens

def _normalize_token_list(raw_tokens):
    tokens = []
    seen = set()

    for t in raw_tokens:
        addr = None
        if isinstance(t, dict):
            addr = t.get("address") or t.get("token_address")
        elif isinstance(t, str):
            addr = t
        if not addr:
            continue
        addr = addr.lower()
        if addr in seen:
            continue
        seen.add(addr)
        tokens.append(addr)

    return tokens

def load_cached_tokens(cache_path):
    try:
        with open(cache_path, 'r') as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            raw_tokens = payload.get("tokens", [])
        else:
            raw_tokens = payload
        return _normalize_token_list(raw_tokens)
    except Exception as e:
        logging.warning(f"Unable to load cached tokens: {e}")
        return []

def save_cached_tokens(cache_path, tokens, network):
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "network": network,
            "tokens": tokens
        }
        with open(cache_path, 'w') as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        logging.warning(f"Unable to save cached tokens: {e}")

def merge_tokens(primary, fallback):
    merged = []
    seen = set()
    for source in (primary, fallback):
        for addr in source:
            addr = addr.lower()
            if addr in seen:
                continue
            seen.add(addr)
            merged.append(addr)
    return merged

def fetch_moralis_holders(address):
    try:
        if not settings.MORALIS_API_KEY:
            return []
        url = f"https://deep-index.moralis.io/api/v2.2/erc20/{address}/owners?chain=celo"
        headers = {"accept": "application/json", "X-API-Key": settings.MORALIS_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(settings.MORALIS_DELAY)
        if response.status_code == 200:
            return response.json().get("result", [])
    except Exception as e:
        logging.warning(f"Error fetching Moralis for {address}: {e}")
    return []

def main():
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    tokens = fetch_trending_tokens(settings.CHAIN)
    if len(tokens) >= MIN_TRENDING_TOKENS:
        save_cached_tokens(TRENDING_CACHE_PATH, tokens, settings.CHAIN)
        logging.info(f"Trending tokens loaded from GeckoTerminal: {len(tokens)}")
    else:
        if tokens:
            logging.warning(f"Trending token list too small ({len(tokens)} < {MIN_TRENDING_TOKENS}); using cache.")
        tokens = []

    cached_tokens = load_cached_tokens(TRENDING_CACHE_PATH)
    if cached_tokens:
        tokens = merge_tokens(tokens, cached_tokens) if tokens else cached_tokens
        logging.info(f"Loaded cached tokens: {len(cached_tokens)}")

    if len(tokens) < MIN_TOKENS:
        logging.warning(f"Token list below minimum ({len(tokens)} < {MIN_TOKENS}).")
        if not tokens:
            logging.error("No tokens available; aborting collection.")
            return

    total = len(tokens)
    estimated_time = total * DELAY_BETWEEN_TOKENS // 60
    logging.info(f"Demarrage collecte de {total} tokens (duree estimee: ~{estimated_time} min)")

    snapshot = {"timestamp": datetime.now(timezone.utc).isoformat(), "tokens": {}}

    for i, address in enumerate(tokens, 1):
        logging.info(f"[{i}/{total}] Collecte pour {address[:10]}...")

        pool_data = fetch_dexscreener(address)
        ohlcv_data = fetch_geckoterminal_ohlcv(address)
        holders_data = fetch_moralis_holders(address)

        snapshot["tokens"][address] = {
            "token_address": address,
            "chain": "celo",
            "pool": pool_data,
            "holders": holders_data,
            "ohlcv": ohlcv_data,
            "indicators": {}
        }

        symbol = pool_data.get("baseToken", {}).get("symbol")
        if not symbol:
            symbol = SYMBOL_FALLBACK.get(address.lower(), "???")

        snapshot["tokens"][address]["symbol_override"] = symbol

        logging.info(f"    {symbol} - {len(holders_data)} holders, {len(ohlcv_data)} candles")

        if i < total:
            logging.info(f"    Pause {DELAY_BETWEEN_TOKENS}s...")
            time.sleep(DELAY_BETWEEN_TOKENS)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(raw_dir, f"snapshot_{timestamp_str}.json")
    with open(filepath, 'w') as f:
        json.dump(snapshot, f, indent=4)

    logging.info(f"Snapshot sauvegarde: {filepath}")

if __name__ == "__main__":
    main()
