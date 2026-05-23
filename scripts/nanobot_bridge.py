import sys
import json
import os

# Add project root to sys.path for local module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.forensics import fetch_trending_tokens, fetch_data
from backend.forensic_engine_v5 import ForensicEngineV5

CHAIN = os.environ.get("CHAIN", "celo")

def run_scan():
    """Performs a live trending scan and returns JSON results for Nanobot"""
    print(f"🔍 Scanning {CHAIN} for trending assets...", file=sys.stderr)
    tokens = fetch_trending_tokens(CHAIN)
    
    if not tokens:
        print(f"⚠️ No trending tokens found on {CHAIN} at this time.", file=sys.stderr)
        print("{}")
        return

    print(f"📊 Found {len(tokens)} trending tokens. Starting forensic analysis...", file=sys.stderr)
    engine = ForensicEngineV5()
    results = {}
    
    for i, t in enumerate(tokens, 1):
        addr = t["address"]
        symbol = t.get("symbol") or "Unknown"
        print(f"[{i}/{len(tokens)}] Analyzing {symbol} ({addr[:10]}...)", file=sys.stderr)
        try:
            data = fetch_data(addr, symbol_override=t.get("symbol"))
            report = engine.analyze(data)
            results[addr] = report.to_dict()
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}", file=sys.stderr)
        
    print(json.dumps(results, indent=2))

def analyze_address(address):
    """Deep dive analysis of a specific address for Nanobot"""
    engine = ForensicEngineV5()
    data = fetch_data(address)
    report = engine.analyze(data)
    print(json.dumps(report.to_dict(), indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/nanobot_bridge.py [scan|analyze] <address>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "scan":
        run_scan()
    elif cmd == "analyze" and len(sys.argv) > 2:
        analyze_address(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
