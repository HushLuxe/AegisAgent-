import os
import json
import requests
from datetime import datetime, timezone
import time
import concurrent.futures
from upstash_redis import Redis
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import relative path trick for Vercel
import sys

KV_URL = os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")
# Local path resolution for Vercel functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from backend.forensic_engine_v5 import ForensicEngineV5
except ImportError:
    # Fallback for different Vercel structure
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from backend.forensic_engine_v5 import ForensicEngineV5

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional in some deployments
    pass

# Configuration from Environment
MORALIS_API_KEY = os.environ.get("MORALIS_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VENICE_API_KEY = os.environ.get("VENICE_API_KEY")
# FORCE Venice branding for Synthesis / Private Agents track
AI_PROVIDER = "venice"

KV_URL = os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")

GECKOTERMINAL_BASE_URL = "https://api.geckoterminal.com/api/v2"
CHAIN = os.environ.get("CHAIN", "celo")
TRENDING_TOKENS_LIMIT = int(os.environ.get("TRENDING_TOKENS_LIMIT", "10"))
TRENDING_DURATION = os.environ.get("TRENDING_DURATION", "24h")
MIN_TRENDING_TOKENS = int(os.environ.get("MIN_TRENDING_TOKENS", "4"))
MIN_TOKENS = int(os.environ.get("MIN_TOKENS", "10"))
TRENDING_CACHE_PATH = os.environ.get("TRENDING_CACHE_PATH", "/tmp/aegis-agent/trending_tokens.json")
ALLOW_STATIC_FALLBACK = os.environ.get("ALLOW_STATIC_FALLBACK", "").lower() in ("1", "true", "yes")

DEXSCREENER_DELAY = float(os.environ.get("DEXSCREENER_DELAY", "0"))
GECKOTERMINAL_DELAY = float(os.environ.get("GECKOTERMINAL_DELAY", "0"))
MORALIS_DELAY = float(os.environ.get("MORALIS_DELAY", "0"))

# Optional static fallback (disabled unless ALLOW_STATIC_FALLBACK=1)
TOKENS = [
    {"address": "0x471ece3750da237f93b8e339c536989b8978a438", "symbol": "CELO"},
    {"address": "0x765de816845861e75a25fca122bb6898b8b1282a", "symbol": "cUSD"},
    {"address": "0xd8763c70d02fdc2d7d39df71c91920c111000000", "symbol": "cEUR"},
    {"address": "0xe8537a3d0523a8b0481f8c9956f2910b00000000", "symbol": "cREAL"},
    {"address": "0x48065fbBE25f71C9282ddf5e1CD6D6A887483D5e", "symbol": "USDT"},
    {"address": "0xcebA9300f2b948710d2653dD7B07f33A8B32118C", "symbol": "USDC"},
    {"address": "0xC668583dcbDc9ae6FA3CE46462758188adfdfC24", "symbol": "stCELO"},
    {"address": "0xD221812de1BD094f35587EE8E174B07B6167D9Af", "symbol": "WETH"},
    {"address": "0x4affD0530739922aa749666E30949AF16768B7bC", "symbol": "G$"},
    {"address": "0x82a605a6D05Ddf568777001010101010101010", "symbol": "PUSDC"}
]


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


def _normalize_tokens(raw_tokens):
    tokens = []
    seen = set()

    for t in raw_tokens:
        addr = None
        symbol = None
        if isinstance(t, dict):
            addr = t.get("address") or t.get("token_address")
            symbol = t.get("symbol") or t.get("ticker")
        elif isinstance(t, str):
            addr = t
        if not addr:
            continue
        addr = addr.lower()
        if addr in seen:
            continue
        seen.add(addr)
        tokens.append({
            "address": addr,
            "symbol": symbol.upper() if symbol else None
        })

    return tokens


def load_cached_tokens(cache_path):
    try:
        with open(cache_path, 'r') as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            raw_tokens = payload.get("tokens", [])
        else:
            raw_tokens = payload
        return _normalize_tokens(raw_tokens)
    except Exception:
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
    except Exception:
        pass


def merge_tokens(primary, fallback, min_total=None):
    merged = []
    seen = set()

    def add(source):
        nonlocal merged
        for t in source:
            addr = t.get("address") if isinstance(t, dict) else None
            symbol = t.get("symbol") if isinstance(t, dict) else None
            if not addr:
                continue
            addr = addr.lower()
            if addr in seen:
                continue
            seen.add(addr)
            merged.append({"address": addr, "symbol": symbol})
            if min_total and len(merged) >= min_total:
                return True
        return False

    add(primary)
    if min_total and len(merged) >= min_total:
        return merged
    add(fallback)
    return merged


def fetch_trending_tokens(network, limit=TRENDING_TOKENS_LIMIT, duration=TRENDING_DURATION):
    url = (
        f"{GECKOTERMINAL_BASE_URL}/networks/{network}/trending_pools"
        f"?include=base_token,quote_token&page=1&duration={duration}"
    )
    try:
        response = requests.get(url, timeout=10, headers={"accept": "application/json"})
        if GECKOTERMINAL_DELAY:
            time.sleep(GECKOTERMINAL_DELAY)
        if response.status_code != 200:
            return []
        payload = response.json()
    except Exception:
        return []

    token_id_to_meta = {}
    for item in payload.get("included", []):
        if item.get("type") != "token":
            continue
        token_id = item.get("id")
        attrs = item.get("attributes", {})
        addr = attrs.get("address") or attrs.get("token_address")
        if not addr and token_id:
            addr = _parse_geckoterminal_token_id(token_id, network)
        if token_id and addr:
            token_id_to_meta[token_id] = {
                "address": addr.lower(),
                "symbol": (attrs.get("symbol") or attrs.get("ticker") or "").upper() or None
            }

    tokens = []
    seen = set()

    def add_token(meta):
        if not meta:
            return
        addr = meta.get("address")
        if not addr:
            return
        if addr in seen:
            return
        seen.add(addr)
        tokens.append({
            "address": addr,
            "symbol": meta.get("symbol")
        })

    for pool in payload.get("data", []):
        relationships = pool.get("relationships", {})
        for key in ("base_token", "quote_token"):
            rel_data = relationships.get(key, {}).get("data")
            token_id = rel_data.get("id") if isinstance(rel_data, dict) else None
            meta = token_id_to_meta.get(token_id) if token_id else None
            if not meta and token_id:
                addr = _parse_geckoterminal_token_id(token_id, network)
                meta = {"address": addr.lower() if addr else None, "symbol": None}
            add_token(meta)
            if len(tokens) >= limit:
                break
        if len(tokens) >= limit:
            break

    return tokens


def fetch_dexscreener_pair(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    try:
        resp = requests.get(url, timeout=6)
        if DEXSCREENER_DELAY:
            time.sleep(DEXSCREENER_DELAY)
        if resp.status_code != 200:
            return {}
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return {}
        return max(pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0))
    except Exception:
        return {}


def fetch_geckoterminal_ohlcv(pool_address, network=CHAIN):
    if not pool_address:
        return []
    url = f"{GECKOTERMINAL_BASE_URL}/networks/{network}/pools/{pool_address}/ohlcv/hour?limit=24"
    try:
        resp = requests.get(url, timeout=8, headers={"accept": "application/json"})
        if GECKOTERMINAL_DELAY:
            time.sleep(GECKOTERMINAL_DELAY)
        if resp.status_code != 200:
            return []
        return resp.json().get("data", {}).get("attributes", {}).get("ohlcv_list", [])
    except Exception:
        return []


def fetch_moralis_holders(address):
    if not MORALIS_API_KEY:
        return []
    try:
        url = f"https://deep-index.moralis.io/api/v2.2/erc20/{address}/owners?chain=celo"
        headers = {"accept": "application/json", "X-API-Key": MORALIS_API_KEY}
        resp = requests.get(url, headers=headers, timeout=8)
        if MORALIS_DELAY:
            time.sleep(MORALIS_DELAY)
        if resp.status_code != 200:
            return []
        return resp.json().get("result", [])
    except Exception:
        return []


def fetch_data(address, symbol_override=None):
    """Fetches raw data for a token using live DEX feeds."""
    pool = fetch_dexscreener_pair(address)
    pool_address = pool.get("pairAddress") if isinstance(pool, dict) else None
    ohlcv = fetch_geckoterminal_ohlcv(pool_address)
    holders = fetch_moralis_holders(address)

    return {
        "token_address": address,
        "chain": CHAIN,
        "pool": pool,
        "holders": holders,
        "ohlcv": ohlcv,
        "symbol_override": symbol_override
    }


def flatten_report(address, report_dict):
    """Flatten report schema to the Dashboard-friendly shape."""
    liq = report_dict.get("liquidity", {})
    flows = report_dict.get("flows", {})
    bf = report_dict.get("bull_flag", {})
    tech = report_dict.get("technical", {})
    forn = report_dict.get("forensic", {})
    conv = report_dict.get("convergence", {})
    raw = report_dict.get("raw_metrics", {})

    return {
        "symbol": report_dict.get("symbol", address[:8]),
        "address": address,
        "chain": report_dict.get("chain", CHAIN),

        "sai": conv.get("sai", 0),
        "sai_label": conv.get("sai_label", ""),
        "phase": conv.get("phase", "UNKNOWN"),
        "cp": conv.get("cp", 0),

        "lfi": liq.get("lfi", 0),
        "lfi_alert": liq.get("lfi_alert", False),
        "lcr": liq.get("lcr", 0),
        "lcr_fragile": liq.get("lcr_fragile", False),
        "lvr": liq.get("lvr", 0),
        "lvr_status": liq.get("lvr_status", ""),
        "dai": liq.get("dai", 0),
        "dai_status": liq.get("dai_status", ""),

        "icr": liq.get("ips_50k", liq.get("ips_10k", 0)),
        "ips_10k": liq.get("ips_10k", 0),
        "ips_50k": liq.get("ips_50k", 0),
        "ips_100k": liq.get("ips_100k", 0),

        "tfa": flows.get("tfa", 0),
        "nbp": flows.get("tfa", 0),
        "tfa_status": flows.get("tfa_status", ""),
        "ev": flows.get("ev", 0),
        "ev_trend": flows.get("ev_trend", ""),
        "ac": flows.get("ac", 0),
        "vwad": flows.get("vwad", 0),
        "flow_classification": flows.get("flow_classification", ""),

        "bull_flag": bf.get("detected", False),
        "bf_retracement": bf.get("retracement_pct", 0),
        "bf_class": bf.get("flag_class", 0),
        "fqs": bf.get("fqs", 0),
        "fqs_label": bf.get("fqs_label", ""),
        "bpi": bf.get("bpi", 0),
        "bpi_label": bf.get("bpi_label", ""),
        "fib_target": bf.get("fib_target_1618", 0),
        "fib_upside_pct": bf.get("fib_upside_pct", 0),
        "pole_high": bf.get("pole_high", 0),
        "pole_low": bf.get("pole_low", 0),
        "squeeze_factor": bf.get("squeeze_factor", 1),

        "rsi_1h": report_dict.get("rsi_1h", tech.get("rsi_1h", 0)),
        "rsi_1d": tech.get("rsi_1d", 0),
        "ber": tech.get("ber", 0),
        "ber_zone": tech.get("ber_zone", ""),
        "rmd": tech.get("rmd", 0),
        "rmd_divergence": tech.get("rmd_divergence", ""),
        "si": tech.get("si", 0),
        "si_status": tech.get("si_status", ""),
        "saturated": tech.get("saturated", False),

        "wcc": forn.get("wcc", 0),
        "wcc_alert": forn.get("wcc_alert", False),
        "scr": forn.get("scr", 0),
        "tci": forn.get("tci", 0),
        "fci": forn.get("fci", 0),
        "top5_pct": forn.get("top5_pct", 0),
        "top10_pct": forn.get("top10_pct", 0),
        "top20_pct": forn.get("top20_pct", 0),

        "price_usd": report_dict.get("price_usd", raw.get("price", 0)),
        "price_change_24h": report_dict.get("price_change_24h", raw.get("price_change_24h", 0)),
        "volume_24h": report_dict.get("volume_24h", raw.get("volume_24h", 0)),
        "liquidity_usd": liq.get("total_usd", raw.get("liquidity", 0)),
        "mcap": report_dict.get("mcap_usd", raw.get("mcap", 0)),
        "buys_24h": int(raw.get("buys", 0)),
        "sells_24h": int(raw.get("sells", 0)),

        "fhs": report_dict.get("fhs", 0),

        "narrative_phase": report_dict.get("narrative_phase", ""),
        "narrative_insight": report_dict.get("narrative_insight", ""),
        "narrative_structure": report_dict.get("narrative_structure", ""),
        "support_key": report_dict.get("support_key", 0),
        "resistance_key": report_dict.get("resistance_key", 0),
        "bailout_recommended": report_dict.get("bailout_recommended", False),

        "alerts": report_dict.get("alerts", []),
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Vercel Serverless Function Entry Point for Python."""

        # Parse query and headers
        url_bits = urlparse(self.path)
        params = parse_qs(url_bits.query)
        is_cron = self.headers.get('x-vercel-cron') == '1'
        is_force = params.get('refresh', ['false'])[0].lower() == 'true'

        # Initialize Redis
        redis = None
        if KV_URL and KV_TOKEN:
            try:
                redis = Redis(url=KV_URL, token=KV_TOKEN)
            except Exception as e:
                print(f"Redis Init Error: {e}")

        # 1. Try to serve from Cache if not forcing/cron
        if not is_cron and not is_force:
            if redis:
                try:
                    cached = redis.get("aegis_forensics")
                    if cached:
                        data = cached if isinstance(cached, str) else json.dumps(cached)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(data.encode('utf-8'))
                        return
                except Exception as e:
                    print(f"Redis Fetch Error: {e}")

        # 2. Run the Pipeline (Slow Path)
        try:
            engine = ForensicEngineV5()
            results = {}

            trending = fetch_trending_tokens(CHAIN)
            tokens = []
            if len(trending) >= MIN_TRENDING_TOKENS:
                save_cached_tokens(TRENDING_CACHE_PATH, trending, CHAIN)
                tokens = trending

            cached_tokens = load_cached_tokens(TRENDING_CACHE_PATH)
            if cached_tokens:
                tokens = merge_tokens(tokens, cached_tokens, MIN_TOKENS)

            if len(tokens) < MIN_TOKENS and ALLOW_STATIC_FALLBACK:
                tokens = merge_tokens(tokens, TOKENS, MIN_TOKENS)

            if len(tokens) < MIN_TOKENS:
                print(f"Warning: token list below minimum ({len(tokens)} < {MIN_TOKENS}).")

            def process_token(t):
                report_data = fetch_data(t["address"], symbol_override=t.get("symbol"))
                report = engine.analyze(report_data)
                report_dict = report.to_dict()
                return t["address"], flatten_report(t["address"], report_dict)

            max_workers = min(len(tokens), 5) if tokens else 1
            pipeline_timeout = None if GROQ_API_KEY else 8

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_addr = {executor.submit(process_token, t): t["address"] for t in tokens}
                if pipeline_timeout:
                    iterator = concurrent.futures.as_completed(future_to_addr, timeout=pipeline_timeout)
                else:
                    iterator = concurrent.futures.as_completed(future_to_addr)

                for future in iterator:
                    try:
                        addr, report_dict = future.result()
                        results[addr] = report_dict
                    except Exception as e:
                        print(f"Error processing token {future_to_addr.get(future)}: {e}")

            final_payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "network": CHAIN.upper(),
                "tokens": results,
                "api_source": "live",
                "ai_enabled": bool(VENICE_API_KEY if AI_PROVIDER == "venice" else GROQ_API_KEY),
                "ai_provider": AI_PROVIDER
            }

            # Save to KV
            if redis:
                try:
                    redis.set("aegis_forensics", json.dumps(final_payload))
                except Exception as e:
                    print(f"Redis Save Error: {e}")

            # Return response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(final_payload).encode('utf-8'))

        except Exception as e:
            print(f"Pipeline Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "fallback": True}).encode('utf-8'))
